---
name: unreal-engine
description: Guide complet d'Unreal Engine 5 — Blueprints, C++ (UE5), Niagara, MetaHuman, World Partition, Gameplay Ability System (GAS), optimisation et déploiement.
---

# Unreal Engine 5 — Guide Complet

Ce skill couvre le développement avec Unreal Engine 5, en Blueprint et C++. À charger pour toute tâche impliquant UE5, le Gameplay Ability System, Niagara, ou le déploiement de jeux Unreal.

---

## 1. Structure du Projet UE5

```
MonJeu/
├── Config/               # Fichiers de configuration (.ini)
│   ├── DefaultEngine.ini
│   ├── DefaultGame.ini
│   └── DefaultInput.ini
├── Content/              # Tout le contenu du jeu
│   ├── Blueprints/       # Blueprints (.uasset)
│   ├── Characters/       # Personnages, animations
│   ├── Environments/     # Maps, niveaux, landscapes
│   ├── FX/               # Niagara, particules, matériaux
│   ├── Audio/            # Sons, musiques, SoundCues
│   ├── UI/               # UMG Widget Blueprints
│   ├── Data/             # DataAssets, DataTables
│   └── MetaHumans/       # Metahumans
├── Source/               # Code C++ UE5
│   └── MonJeu/
│       ├── MonJeu.Build.cs
│       ├── Public/       # Headers (.h)
│       └── Private/      # Implémentations (.cpp)
└── MonJeu.uproject       # Fichier projet
```

---

## 2. C++ UE5 — Patterns Essentiels

### Actor de base

```cpp
// Source/MonJeu/Public/Personnage.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Personnage.generated.h"

UCLASS()
class MONJEU_API APersonnage : public ACharacter
{
    GENERATED_BODY()

public:
    APersonnage();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
    float Sante = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
    float VitesseMarche = 600.0f;

    UFUNCTION(BlueprintCallable, Category = "Combat")
    void SubirDegats(float Degats);

private:
    void DeplacerAvant(float Valeur);
    void DeplacerDroite(float Valeur);
};
```

### Implémentation

```cpp
// Source/MonJeu/Private/Personnage.cpp
#include "Personnage.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"

APersonnage::APersonnage()
{
    PrimaryActorTick.bCanEverTick = true;
}

void APersonnage::BeginPlay()
{
    Super::BeginPlay();

    // Configurer Enhanced Input
    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
        {
            Subsystem->AddMappingContext(InputMapping, 0);
        }
    }
}

void APersonnage::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    if (UEnhancedInputComponent* EnhancedInput = Cast<UEnhancedInputComponent>(PlayerInputComponent))
    {
        EnhancedInput->BindAction(InputActionMove, ETriggerEvent::Triggered, this, &APersonnage::DeplacerAvant);
    }
}

void APersonnage::SubirDegats(float Degats)
{
    Sante = FMath::Clamp(Sante - Degats, 0.0f, 100.0f);
    if (Sante <= 0.0f)
    {
        Die();
    }
}
```

---

## 3. Gameplay Ability System (GAS)

GAS est le système de capacités natif d'UE5 pour les RPG, MOBAs, et jeux d'action.

```cpp
// Attributs
UCLASS()
class UMonAttributeSet : public UAttributeSet
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadOnly, ReplicatedUsing = OnRep_Sante, Category = "Attributs")
    FGameplayAttributeData Sante;
    UPROPERTY(BlueprintReadOnly, ReplicatedUsing = OnRep_Mana, Category = "Attributs")
    FGameplayAttributeData Mana;
    UPROPERTY(BlueprintReadOnly, ReplicatedUsing = OnRep_Endurance, Category = "Attributs")
    FGameplayAttributeData Endurance;

    // Réplications
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
};
```

### Créer une GameplayAbility

```cpp
UCLASS()
class UCompBouleDeFeu : public UGameplayAbility
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    TSubclassOf<AActor> ProjectileClasse;

    virtual void ActivateAbility(
        const FGameplayAbilitySpecHandle Handle,
        const FGameplayAbilityActorInfo* ActorInfo,
        const FGameplayAbilityActivationInfo ActivationInfo,
        const FGameplayEventData* TriggerEventData
    ) override;
};
```

---

## 4. Niagara — Système de Particules

### Création via script (C++)

```cpp
UNiagaraComponent* CompParticules = CreateDefaultSubobject<UNiagaraComponent>(TEXT("Particules"));
CompParticules->SetAsset(Charger<UNiagaraSystem>("/Game/FX/Explosion.Explosion"));
CompParticules->SetVariableFloat("DureeExplosion", 2.0f);
CompParticules->Activate();
```

### Niagara Paramètres clés
- **Emitter** → GPU vs CPU (GPU = 100x+ particules, mais sans collision complexe)
- **Parameter Bindings** → Lier depuis code C++ / Blueprint
- **Data Interfaces** → Event Sourcing, Collision, Grid2D/3D
- **Modules personnalisés** → HLSL dans Niagara Script

---

## 5. World Partition (Mondes Ouverts)

```ini
; DefaultEngine.ini
[WorldPartition]
bEnableWorldPartition=true
WorldPartitionGridSize=25600
HLODLayer=HLOD_Med

; Streaming
[ConsoleVariables]
wp.Runtime.StreamingEnabled=1
wp.Runtime.MaxLoadDistance=50000
wp.Runtime.MinUnloadDistance=60000
```

### Landscape et Foliage
```cpp
// Génération procédurale de foliage
ALandscapeProxy* Landscape = GetWorld()->SpawnActor<ALandscapeProxy>();
Landscape->SetActorLocation(FVector::ZeroVector);
// Utiliser LandscapeGrassType pour des mixed grass meshes
```

---

## 6. MetaHuman

### Pipeline d'import
1. Créer dans MetaHuman Creator (quixel.com/metahuman)
2. Exporter → Bridge (Quixel) → UE5 direct
3. Utiliser **MetaHuman Animator** pour capture faciale (iPhone LiDAR)
4. Body: **MetaHuman Rig** → retargetting d'animations

```cpp
// Contrôler un MetaHuman via code
AMetaHuman* MH = Cast<AMetaHuman>(Personnage);
if (MH)
{
    MH->SetExpression(EExpression::Joie, 0.8f);
    MH->SetBlinkState(true);
}
```

---

## 7. Optimisation UE5

### Console variables clés
```
# Visualiser les coûts
stat fps
stat unit
stat gpu
r.Streaming.PoolSize 500          # Pool de textures (Mo)
r.ScreenPercentage 100            # Résolution interne (scaling)
foliage.DensityScale 0.5          # Densité foliage
r.ShadowQuality 3                 # Qualité ombres (0-5)
r.AmbientOcclusionLevels 3        # AO
r.Lumen. Reflections.Enable 0     # Désactiver Lumen (fallback SSR)
r.Nanite 1                        # Nanite activé
r.VirtualTexture 1                # Streaming textures
```

### Checklist optimisation UE5
1. **Nanite** : activé par défaut sur tous les modèles >100k tris
2. **Lumen** : désactiver sur mobile/VR (SSR fallback)
3. **World Partition** : obligatoire pour mondes ouverts > 2 km²
4. **HLOD** : Hierarchical LOD pour le streaming distant
5. **Texture Streaming Pool** : ajuster selon RAM GPU disponible
6. **Anim Blueprint** : optimiser les blendspaces (limiter nodes évalués)
7. **Niagara GPU** : privilégier GPU emit pour VFX lourds
8. **Dynamic Resolution** : `r.DynamicRes.OperationMode 2`

---

## 8. Build et Déploiement

```bash
# Build depuis la CLI Unreal
/chemin/UE_5.4/Engine/Build/BatchFiles/RunUAT.sh BuildCookRun \
    -project=/chemin/MonJeu.uproject \
    -noP4 -platform=Linux -clientconfig=Shipping \
    -serverconfig=Shipping -cook -allmaps -build -stage -pak -archive \
    -archivedirectory=./Build/

# Packaging
# Éditeur → File → Package Project → Windows/Linux/Android/iOS
```

### Plugin Build Configuration

```cpp
// MonJeu.Build.cs
using UnrealBuildTool;

public class MonJeu : ModuleRules
{
    public MonJeu(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core", "CoreUObject", "Engine", "InputCore",
            "EnhancedInput", "GameplayAbilities", "GameplayTags",
            "GameplayTasks", "Niagara", "Metahuman", "UMG",
            "NavigationSystem", "AIModule"
        });
    }
}
```

---

## 9. Pièges Courants

- **UObject sans UCLASS() macro** → crash linker UE5
- **Garbage Collection** : pas de raw `new` → `NewObject<T>()` ou `CreateDefaultSubobject<T>()`
- **Enhanced Input** : remplacer `SetupPlayerInputComponent` classique, OBLIGATOIRE pour UE5.3+
- **GAS replication** : déclarer `ReplicatedUsing` sur chaque attribut de l'AttributeSet
- **World Partition streaming** : charger les cellules VOISINES, pas toutes d'un coup
- **MetaHuman neck seam** : résoudre via "Merge Materials" dans le MetaHuman component
- **Niagara GPU collision** : pas de collision complexe sur emit GPU → utiliser CPU à la place
- **Build takes ages** : utiliser `-nobuild` pour l'éditeur, `-distribution` pour shipping
