---
name: networking-multiplayer
description: Réseau et multijoueur pour jeux vidéo — architecture client-serveur, prédiction, réconciliation, lag compensation, rollback, Steamworks, Photon, Mirror, Netcode, ENet, WebRTC, anti-triche.
tags: [networking, multiplayer, prediction, reconciliation, lag-compensation, steamworks, photon, mirror, netcode, enet, webrtc]
---

# Networking & Multiplayer — Guide Complet

Ce skill couvre l'architecture réseau pour jeux vidéo multijoueurs, de l'autorité serveur à la prédiction client. À charger pour toute tâche impliquant le développement de fonctionnalités multijoueur, la synchronisation d'état, ou l'optimisation réseau.

---

## 1. Architecture Réseau — Choix Fondamentaux

### Modèles d'Autorité

| Modèle | Avantages | Inconvénients | Utilisation |
|--------|-----------|---------------|-------------|
| **Authoritative Server** | Anti-triche, contrôle total | Latence, coût serveur | FPS, MOBA, RTS |
| **Listen Server** | Pas de serveur dédié | Host advantage | Casual, coop |
| **P2P** | Pas de serveur, décentralisé | Cheating, NAT traversal | Fighting, RTS lockstep |
| **Dedicated Server** | Fair, scalable | Coût d'infra | AAA, competitive |
| **P2P avec relay** | Déploiement simple | Coût bande passante | Party games, Among Us |

### Schéma d'Architecture

```text
Client A                    Serveur                    Client B
   │                          │                          │
   │── Input (15-30 Hz) ────→│ ←── Input (15-30 Hz) ──│
   │                          │                          │
   │←── World State (20 Hz) ─│── World State (20 Hz) ─→│
   │                          │                          │
   │     ┌──────────────┐     │     ┌──────────────┐     │
   │     │ Prédiction   │     │     │ Prédiction   │     │
   │     │ locale       │     │     │ locale       │     │
   │     └──────────────┘     │     └──────────────┘     │
```

---

## 2. Prédiction Client et Réconciliation

### Architecture de Prédiction Client (FPS)

```csharp
public class MovementPrediction : MonoBehaviour
{
    private struct State
    {
        public Vector3 Position;
        public Vector3 Velocity;
        public float Timestamp;
    }

    private Queue<InputSnapshot> _pendingInputs = new();
    private State _predictedState;
    private State _authoritativeState;

    public void SendInput(InputSnapshot input)
    {
        _pendingInputs.Enqueue(input);
        _predictedState = Predict(_predictedState, input);
        NetworkManager.Send(MsgType.PlayerInput, input);
    }

    public void OnServerState(ServerState state)
    {
        _authoritativeState = new State
        {
            Position = state.Position,
            Velocity = state.Velocity,
            Timestamp = state.ServerTime
        };

        // Réconciliation
        _predictedState = _authoritativeState;

        while (_pendingInputs.Count > 0 &&
               _pendingInputs.Peek().SequenceNumber <= state.LastProcessedInput)
        {
            _pendingInputs.Dequeue();
        }

        foreach (var input in _pendingInputs)
            _predictedState = Predict(_predictedState, input);
    }

    private State Predict(State current, InputSnapshot input)
    {
        return new State
        {
            Position = current.Position + input.Movement * _speed * Time.fixedDeltaTime,
            Velocity = input.Movement * _speed,
            Timestamp = current.Timestamp + Time.fixedDeltaTime
        };
    }

    void Update()
    {
        float lerp = 0.1f;
        transform.position = Vector3.Lerp(transform.position, _predictedState.Position, lerp);
    }
}
```

### Lag Compensation — Server-Side Rewind

```csharp
public class LagCompensation : MonoBehaviour
{
    private struct HistoricState
    {
        public Collider Collider;
        public Vector3 Position;
        public Quaternion Rotation;
        public float Time;
    }

    private Dictionary<int, Queue<HistoricState>> _colliderHistory = new();
    private const float REWIND_WINDOW = 0.5f;

    public void RecordFrame()
    {
        foreach (var player in PlayerManager.AllPlayers)
        {
            var history = _colliderHistory.GetOrCreate(player.NetId);
            history.Enqueue(new HistoricState
            {
                Collider = player.Hitbox,
                Position = player.transform.position,
                Rotation = player.transform.rotation,
                Time = Time.time
            });
            while (history.Count > 0 && history.Peek().Time < Time.time - REWIND_WINDOW)
                history.Dequeue();
        }
    }

    public bool TryShot(float clientTimestamp, Ray shotRay, out Player hitPlayer)
    {
        hitPlayer = null;
        float rewindTime = Time.time - (NetworkManager.ServerTime - clientTimestamp) / 2f;

        foreach (var kvp in _colliderHistory)
        {
            // Trouver l'état le plus proche du rewindTime
            // Tester le raycast contre cette position historique
        }
        return hitPlayer != null;
    }
}
```

---

## 3. Snapshot Interpolation et Extrapolation

```csharp
public class SnapshotInterpolation : MonoBehaviour
{
    private struct Snapshot
    {
        public Vector3 Position;
        public Quaternion Rotation;
        public float ServerTime;
    }

    private Queue<Snapshot> _buffer = new();
    private const int BUFFER_SIZE = 3;
    private const float INTERPOLATION_DELAY = 0.1f;
    private Vector3 _lastKnownVelocity;

    void Update()
    {
        if (_buffer.Count >= BUFFER_SIZE)
        {
            float renderTime = (float)NetworkManager.LocalTime - INTERPOLATION_DELAY;
            while (_buffer.Count >= 2 && _buffer.Peek().ServerTime <= renderTime)
                _buffer.Dequeue();

            if (_buffer.Count < 2) return;

            var prev = _buffer.Peek();
            var next = _buffer.Skip(1).First();
            float t = Mathf.Clamp01((renderTime - prev.ServerTime) / (next.ServerTime - prev.ServerTime));

            transform.position = Vector3.Lerp(prev.Position, next.Position, t);
            transform.rotation = Quaternion.Slerp(prev.Rotation, next.Rotation, t);
            _lastKnownVelocity = (transform.position - _previousPosition) / Time.deltaTime;
        }
        else
        {
            // Extrapolation avec drag
            transform.position += _lastKnownVelocity * Time.deltaTime;
            _lastKnownVelocity *= (1f - 2f * Time.deltaTime);
        }
        _previousPosition = transform.position;
    }
}
```

---

## 4. Netcode Solutions par Moteur

### Unity Netcode for GameObjects

```csharp
using Unity.Netcode;

public class PlayerNetcode : NetworkBehaviour
{
    public NetworkVariable<float> Health = new(100f,
        NetworkVariableReadPermission.Everyone,
        NetworkVariableWritePermission.Server);

    public override void OnNetworkSpawn()
    {
        Health.OnValueChanged += (oldVal, newVal) => UpdateHealthBar(newVal);
    }

    [ServerRpc]
    public void ShootServerRpc(Vector3 target)
    {
        var bullet = Instantiate(bulletPrefab, gunPoint.position, Quaternion.LookRotation(target));
        bullet.GetComponent<NetworkObject>().Spawn();
    }

    [ClientRpc]
    public void ExplosionClientRpc(Vector3 position)
    {
        Instantiate(explosionEffect, position, Quaternion.identity);
    }

    void Update()
    {
        if (!IsOwner) return;
        // Mouvement local
    }
}
```

### Mirror (Unity)

```csharp
using Mirror;

public class PlayerMirror : NetworkBehaviour
{
    [SyncVar(hook = nameof(OnHealthChanged))]
    public float Health = 100f;

    [Command]
    public void CmdShoot(Vector3 direction)
    {
        Bullet bullet = Instantiate(bulletPrefab, firePoint.position, Quaternion.LookRotation(direction));
        NetworkServer.Spawn(bullet.gameObject);
    }

    [ClientRpc]
    public void RpcExplosion(Vector3 pos)
    {
        Instantiate(explosionFx, pos, Quaternion.identity);
    }

    [Client]
    void OnHealthChanged(float oldVal, float newVal) => UpdateHealthBar(newVal);

    [Server]
    public void TakeDamage(float damage) => Health -= damage;
}
```

### Godot — ENet Multiplayer

```gdscript
# Server.gd
extends Node

@export var port := 8080
@export var max_players := 8

func start_server():
    var peer := ENetMultiplayerPeer.new()
    peer.create_server(port, max_players)
    multiplayer.multiplayer_peer = peer
    multiplayer.peer_connected.connect(_player_connected)
    print("Serveur démarré sur ", port)

func _player_connected(id: int):
    var player = preload("res://scenes/Player.tscn").instantiate()
    player.name = str(id)
    player.set_multiplayer_authority(id)
    add_child(player)

@rpc("authority", "call_local", "reliable")
func sync_world_state(state: Dictionary):
    pass

@rpc("any_peer", "call_remote", "unreliable")
func send_input(input: Dictionary):
    pass
```

### Unreal Engine 5 — Enhanced Replication

```cpp
UCLASS()
class APersonnageMulti : public ACharacter
{
    GENERATED_BODY()
public:
    UPROPERTY(ReplicatedUsing = OnRep_Health)
    float Health = 100.0f;

    UFUNCTION(Server, Reliable, WithValidation)
    void Server_Shoot(FVector Direction);

    UFUNCTION(Client, Unreliable)
    void Client_PlayImpact(FVector Location);

    UFUNCTION(NetMulticast, Reliable)
    void Multicast_Explosion(FVector Location);

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProps>& Out) const override;
    UFUNCTION() void OnRep_Health();
};

void APersonnageMulti::GetLifetimeReplicatedProps(TArray<FLifetimeProps>& Out) const
{
    Super::GetLifetimeReplicatedProps(Out);
    DOREPLIFETIME(APersonnageMulti, Health);
}

bool APersonnageMulti::Server_Shoot_Validate(FVector Direction)
{
    return !Direction.IsZero(); // Anti-cheat validation
}

void APersonnageMulti::Server_Shoot_Implementation(FVector Direction)
{
    FActorSpawnParameters Params;
    Params.Instigator = this;
    GetWorld()->SpawnActor<AProjectile>(ProjectileClass, GunLocation(), Direction.Rotation(), Params);
}
```

---

## 5. Steamworks (SteamNetworkingSockets)

```cpp
#include "steam/steamnetworkingsockets.h"

class GameNetworkManager
{
    HSteamListenSocket m_hListenSocket;
    HSteamNetConnection m_hConnection;
    ISteamNetworkingSockets* m_pInterface;

public:
    bool InitServer()
    {
        SteamDatagramErrMsg errMsg;
        if (!GameNetworkingSockets_Init(nullptr, errMsg)) return false;

        m_pInterface = SteamNetworkingSockets();
        SteamNetworkingIPAddr serverAddr;
        serverAddr.Clear();
        serverAddr.m_port = 27015;

        m_hListenSocket = m_pInterface->CreateListenSocketIP(serverAddr, 1, nullptr);
        return m_hListenSocket != k_HSteamListenSocket_Invalid;
    }

    bool ConnectToServer(const char* addr)
    {
        SteamNetworkingIPAddr serverAddr;
        serverAddr.ParseString(addr);
        m_hConnection = m_pInterface->ConnectByIPAddress(serverAddr, 0, nullptr);
        return m_hConnection != k_HSteamNetConnection_Invalid;
    }

    void Poll()
    {
        ISteamNetworkingMessage* pMsg = nullptr;
        while (m_pInterface->ReceiveMessagesOnConnection(m_hConnection, &pMsg, 1) > 0)
        {
            ProcessMessage(pMsg->m_pData, pMsg->m_cbSize);
            pMsg->Release();
        }
    }
};
```

---

## 6. Rollback Netcode (Jeux de Combat)

```csharp
public class RollbackSystem
{
    public struct FrameState
    {
        public Vector2 Position;
        public Vector2 Velocity;
        public float Health;
        public int FrameNumber;
        public int ActionId;
    }

    private FrameState[] _frameBuffer = new FrameState[120];
    private FrameState _currentState;
    private Queue<InputFrame> _inputHistory = new();
    private int _currentFrame;

    public void AdvanceFrame(InputFrame input)
    {
        _currentFrame++;
        _inputHistory.Enqueue(input);
        _currentState.FrameNumber = _currentFrame;
        _currentState.Position = ApplyPhysics(_currentState.Position, input);
        _frameBuffer[_currentFrame % _frameBuffer.Length] = _currentState;
    }

    public void Rollback(int toFrame, InputFrame correctInput)
    {
        _currentState = _frameBuffer[toFrame % _frameBuffer.Length];
        _currentFrame = toFrame;
        _inputHistory.Dequeue();
        _inputHistory.Enqueue(correctInput);
        foreach (var input in _inputHistory)
            AdvanceFrame(input);

        OnRollbackPerformed?.Invoke(_currentFrame, toFrame);
    }
}
```

---

## 7. Interest Management et Bandwidth

```csharp
public class InterestManager : MonoBehaviour
{
    private const float CELL_SIZE = 100f;
    private Dictionary<Vector2Int, HashSet<NetworkObject>> _grid = new();

    public HashSet<NetworkObject> GetRelevantObjects(Vector3 pos)
    {
        Vector2Int cell = WorldToCell(pos);
        var relevant = new HashSet<NetworkObject>();
        for (int x = -1; x <= 1; x++)
            for (int z = -1; z <= 1; z++)
                if (_grid.TryGetValue(new Vector2Int(cell.x + x, cell.y + z), out var objs))
                    relevant.UnionWith(objs);
        return relevant;
    }

    private Vector2Int WorldToCell(Vector3 pos) => new(
        Mathf.FloorToInt(pos.x / CELL_SIZE),
        Mathf.FloorToInt(pos.z / CELL_SIZE)
    );
}
```

---

## 8. Anti-Triche Côté Serveur

```cpp
bool Server_ValidateMovement(Player* p, Vector3 newPos, float clientTime)
{
    float dist = Vector3::Dist(p->LastPosition, newPos);
    float maxDist = p->Speed * (GetWorldTime() - clientTime) * 1.5f;

    if (dist > maxDist) return false; // Speed hack

    if (Physics::Linecast(p->LastPosition, newPos, WallMask))
        return false; // Wall hack

    if (clientTime < p->LastClientTime) return false; // Temps qui recule

    return true;
}
```

---

## 9. Pièges Courants

- **Déterminisme brisé** : Toujours timestep fixe, jamais `Time.deltaTime` variable.
- **Pas de buffer d'interpolation** : Minimum 2-3 snapshots ou saccades garanties.
- **Réconciliation absente** : Le client prédit sans correction → dérive infinie.
- **RPC Reliable en masse** : Backpressure → lag. Utiliser Unreliable pour les tirs/mouvements.
- **Autorité client pour les dégâts** : Toujours serveur authoritative.
- **Speed hack** : Toujours valider distance/vélocité côté serveur.
- **Pas de lag compensation** : Le joueur avec ping 200ms ne peut toucher personne.
- **Interest Management absent** : Saturé au-delà de 30 joueurs.
- **Serialisation naive** : Floats en string → overhead énorme. Binaire toujours.
- **NAT traversal ignoré** : Les joueurs derrière un NAT strict ne peuvent pas se connecter.