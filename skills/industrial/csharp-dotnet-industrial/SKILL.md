---
name: csharp-dotnet-industrial
description: "Développer en C# pour l'intégration MES et les HMIs Windows."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [windows, linux]
metadata:
  tags: [csharp, dotnet, opc-ua, ads, mes, snap7, plctag, wpf, mvvm, database, industrial-integration]
  related_skills: [sql-for-industrial-systems, ot-it-integration-languages, scada-hmi-programming-languages]
---

# Développement C# / .NET pour l'Intégration OT-IT et les HMIs Industrielles

Cette compétence encadre l'utilisation de C# et du framework .NET pour concevoir des applications de supervision (HMI), connecter des équipements industriels aux systèmes MES/ERP (OT-IT), et manipuler des protocoles de communication natifs.

---

## 1. Client OPC UA Robuste avec Reconnexion Automatique (.NET Core)

En production, un client OPC UA ne doit jamais perdre sa connexion de manière définitive. Le code ci-dessous utilise le SDK officiel `OPCFoundation.NetStandard.Opc.Ua` et implémente un gestionnaire robuste.

```csharp
using System;
using System.Threading;
using System.Threading.Tasks;
using Opc.Ua;
using Opc.Ua.Client;
using Opc.Ua.Configuration;

public class EVAOpcClient
{
    private Session _session;
    private readonly string _endpointUrl;
    private readonly ApplicationConfiguration _config;

    public EVAOpcClient(string endpointUrl)
    {
        _endpointUrl = endpointUrl;
        _config = CreateOpcConfiguration();
    }

    private ApplicationConfiguration CreateOpcConfiguration()
    {
        var config = new ApplicationConfiguration()
        {
            ApplicationName = "EVA.OpcClient",
            ApplicationType = ApplicationType.Client,
            ApplicationConfiguration = new ClientConfiguration { DefaultSessionTimeout = 60000 },
            SecurityConfiguration = new SecurityConfiguration
            {
                AutoAcceptUntrustedCertificates = true,
                RejectSHA1SignedCertificates = false
            },
            TransportQuotas = new TransportQuotas { OperationTimeout = 15000 }
        };
        config.Validate(ApplicationType.Client).GetAwaiter().GetResult();
        return config;
    }

    public async Task ConnectAsync(CancellationToken ct)
    {
        var endpoint = new ConfiguredEndpoint(null, 
            CoreClientUtils.SelectEndpoint(_endpointUrl, useSecurity: false), 
            EndpointConfiguration.Create(_config));

        while (!ct.IsCancellationRequested)
        {
            try
            {
                Console.WriteLine($"Connexion à {_endpointUrl}...");
                _session = await Session.Create(_config, endpoint, false, "EVASession", 60000, null, null);
                _session.KeepAlive += OnSessionKeepAlive;
                Console.WriteLine("Connecté avec succès au serveur OPC UA !");
                break;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Échec de connexion : {ex.Message}. Tentative dans 5 secondes...");
                await Task.Delay(5000, ct);
            }
        }
    }

    private void OnSessionKeepAlive(ISession session, KeepAliveEventArgs e)
    {
        if (e.Status != KeepAliveStatus.Good)
        {
            Console.WriteLine($"KeepAlive incorrect : {e.Status}. Tentative de reconnexion...");
            Task.Run(() => ConnectAsync(CancellationToken.None));
        }
    }

    public async Task<DataValue> ReadNodeAsync(string nodeIdStr)
    {
        if (_session == null || !_session.Connected)
            throw new InvalidOperationException("Client non connecté.");

        var nodeId = new NodeId(nodeIdStr);
        var nodesToRead = new ReadValueIdCollection {
            new ReadValueId { NodeId = nodeId, AttributeId = Attributes.Value }
        };

        var response = await _session.ReadAsync(null, 0, TimestampsToReturn.Both, nodesToRead, CancellationToken.None);
        return response.Results[0];
    }
}
```

---

## 2. Communication Automate Directe (Drivers ADS & S7)

### Beckhoff TwinCAT ADS (Lecture et Notification d'Événements)
Pour éviter de poller le PLC en permanence, on utilise l'enregistrement de notifications d'ADS (`TwinCAT.Ads`).

```csharp
using System;
using TwinCAT.Ads;

public class TwinCatManager : IDisposable
{
    private AdsClient _client;
    private uint _notificationHandle;

    public void Initialize(string netId, int port)
    {
        _client = new AdsClient();
        _client.Connect(netId, port);

        // Enregistrement d'une notification sur changement de variable PLC
        // Cycle de vérification de 100ms, transmission immédiate sur changement de valeur
        _notificationHandle = _client.AddDeviceNotification(
            "GVL.TemperatureFour", 
            new TypeMarshaler(typeof(float)), 
            new NotificationSettings(AdsTransMode.OnChange, 100, 0), 
            null
        );

        _client.AdsNotification += OnAdsNotificationReceived;
    }

    private void OnAdsNotificationReceived(object sender, AdsNotificationEventArgs e)
    {
        if (e.UserData is float temp)
        {
            Console.WriteLine($"[ALERT] Changement de température reçu : {temp} °C");
        }
    }

    public void Dispose()
    {
        if (_client != null)
        {
            if (_notificationHandle != 0)
                _client.DeleteDeviceNotification(_notificationHandle);
            _client.Disconnect();
            _client.Dispose();
        }
    }
}
```

---

## 3. Architecture MVVM pour HMI Industrielle (WPF / .NET 8)

En atelier de fabrication, les HMIs WPF doivent être hautement réactives. Le modèle ViewModel ci-dessous met à jour l'interface de manière asynchrone sans bloquer le thread principal.

```csharp
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;

public class MainViewModel : INotifyPropertyChanged
{
    private float _pressionCuve;
    private string _statutConnexion = "Déconnecté";

    public float PressionCuve
    {
        get => _pressionCuve;
        set
        {
            _pressionCuve = value;
            OnPropertyChanged();
        }
    }

    public string StatutConnexion
    {
        get => _statutConnexion;
        set
        {
            _statutConnexion = value;
            OnPropertyChanged();
        }
    }

    public event PropertyChangedEventHandler PropertyChanged;

    protected void OnPropertyChanged([CallerMemberName] string propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }

    // Boucle d'acquisition asynchrone lancée au démarrage de la fenêtre
    public async Task StartAcquisitionLoopAsync(EVAOpcClient client, CancellationToken ct)
    {
        StatutConnexion = "En cours de connexion...";
        await client.ConnectAsync(ct);
        StatutConnexion = "Connecté";

        while (!ct.IsCancellationRequested)
        {
            try
            {
                var data = await client.ReadNodeAsync("ns=2;s=Pression_Cuve_1");
                if (data.Value is float pression)
                {
                    PressionCuve = pression;
                }
                await Task.Delay(500, ct); // Fréquence de rafraîchissement 500ms
            }
            catch
            {
                StatutConnexion = "Perte de liaison automate !";
                await client.ConnectAsync(ct);
            }
        }
    }
}
```

---

## 4. Intégration de Bases de Données (MES / Traçabilité) via Dapper

Dapper est préféré à Entity Framework dans les environnements industriels pour des questions de performances brutes de requêtage SQL.

```csharp
using System;
using System.Data.SqlClient;
using Dapper;

public class ProductionLogger
{
    private readonly string _connectionString;

    public ProductionLogger(string connectionString)
    {
        _connectionString = connectionString;
    }

    public void LogLotProduction(string lotId, float poidsMesure, string operateur)
    {
        const string query = @"
            INSERT INTO T_Tracabilite_Lots (ID_Lot, Date_Enregistrement, Poids, Operateur, Statut)
            VALUES (@LotId, @DateEnreg, @Poids, @Operateur, @Statut);";

        using (var connection = new SqlConnection(_connectionString))
        {
            connection.Open();
            connection.Execute(query, new {
                LotId = lotId,
                DateEnreg = DateTime.Now,
                Poids = poidsMesure,
                Operateur = operateur,
                Statut = poidsMesure >= 10.0f ? "CONFORME" : "REBUT"
            });
        }
    }
}
```
