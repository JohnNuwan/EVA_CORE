---
name: game-ui
description: Interface utilisateur pour jeux vidéo — uGUI, UMG, Godot Control, Dear ImGui, HUD, inventaire, menus, world space UI, UI animation, responsive, accessibilité, minimap, localisation, optimisation UI.
tags: [game-ui, ugui, umg, godot-control, dear-imgui, hud, inventory, menu, world-space-ui, ui-animation, accessibility, minimap, localization]
---

# Game UI — Guide Complet

Ce skill couvre la conception et le développement d'interfaces utilisateur pour jeux vidéo. À charger pour toute tâche impliquant HUD, menus, inventaire, UI world-space, ou systèmes UI dans Unity/Unreal/Godot.

---

## 1. Frameworks UI par Moteur

| Moteur | Framework | Usage | Points Forts |
|--------|-----------|-------|-------------|
| **Unity** | uGUI (Canvas) | Standard | Ancres, Canvas scaler, EventSystem |
| **Unity** | UI Toolkit | Éditeur/UI complexe | USS/UXML, data binding |
| **Unreal** | UMG/Slate | Tout Unreal | Widget Blueprint, animation |
| **Godot** | Control Nodes | Tout Godot | Theme, StyleBox, containers |
| **Custom** | Dear ImGui | Outils, debug | Immédiat mode, zéro setup |
| **Web** | Coherent GT | UI HTML | Design web, full JS |

---

## 2. Architecture UI — Patterns

### MVC (Model-View-Controller)

```csharp
// MODEL — données pures
public class PlayerStats : MonoBehaviour
{
    public int Health { get; private set; } = 100;
    public int MaxHealth = 100;
    public int Score { get; private set; }

    public event System.Action<int, int> OnHealthChanged;
    public event System.Action<int> OnScoreChanged;

    public void TakeDamage(int damage)
    {
        Health = Mathf.Max(0, Health - damage);
        OnHealthChanged?.Invoke(Health, MaxHealth);
    }

    public void AddScore(int points)
    {
        Score += points;
        OnScoreChanged?.Invoke(Score);
    }
}

// VIEW — affichage seulement
public class HealthBarView : MonoBehaviour
{
    [SerializeField] private Image _fillImage;
    [SerializeField] private Text _healthText;

    public void UpdateHealth(int current, int max)
    {
        _fillImage.fillAmount = (float)current / max;
        _healthText.text = $"{current}/{max}";
    }
}

// CONTROLLER — relie le modèle à la vue
public class HUDController : MonoBehaviour
{
    [SerializeField] private PlayerStats _stats;
    [SerializeField] private HealthBarView _healthBar;

    void Start()
    {
        _stats.OnHealthChanged += _healthBar.UpdateHealth;
        _stats.OnScoreChanged += UpdateScoreDisplay;
        // Initialisation
        _healthBar.UpdateHealth(_stats.Health, _stats.MaxHealth);
    }
}
```

### Data Binding (UI Toolkit)

```xml
<!-- Unity UI Toolkit — UXML -->
<ui:UXML xmlns:ui="UnityEngine.UIElements">
  <ui:Label text="Score: {score}" binding-path="Score" />
  <ui:ProgressBar low-value="0" high-value="100"
                  binding-path="Health" />
</ui:UXML>
```

### Event-Driven UI

```csharp
// Système d'événements centralisé
public static class GameEvents
{
    public static event System.Action<int> OnScoreChanged;
    public static event System.Action<float> OnHealthChanged;
    public static event System.Action<Item> OnItemCollected;
    public static event System.Action<GameState> OnGameStateChanged;

    public static void ScoreChanged(int score) => OnScoreChanged?.Invoke(score);
    public static void HealthChanged(float health) => OnHealthChanged?.Invoke(health);
    public static void ItemCollected(Item item) => OnItemCollected?.Invoke(item);
    public static void GameStateChanged(GameState state) => OnGameStateChanged?.Invoke(state);
}

// Émetteur
public class ScorePickup : MonoBehaviour
{
    public int points = 100;
    void OnTriggerEnter() => GameEvents.ScoreChanged(points);
}

// Récepteur (UI)
public class ScoreDisplay : MonoBehaviour
{
    [SerializeField] private Text _scoreText;

    void OnEnable() => GameEvents.OnScoreChanged += UpdateScore;
    void OnDisable() => GameEvents.OnScoreChanged -= UpdateScore;

    void UpdateScore(int score)
    {
        _scoreText.text = score.ToString("N0");
        // Animation de score qui pop
        StartCoroutine(AnimateScorePop());
    }
}
```

---

## 3. Canvas et Layout (Unity uGUI)

### Canvas Scalers (Résolution Indépendante)

```csharp
// Configuration Canvas Scaler
// Reference Resolution: 1920x1080 (ou 1280x720 pour mobile)
// Screen Match Mode:
//   - Match Width or Height: 0.5 (mix)
//   - Expand: UI s'adapte sans dépasser
//   - Shrink: UI remplit toujours l'écran

// Canvas Scaler via code
void SetupCanvas(CanvasScaler scaler)
{
    scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
    scaler.referenceResolution = new Vector2(1920, 1080);
    scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
    scaler.matchWidthOrHeight = 0.5f; // 0 = width, 1 = height

    // Pixel perfect (pour pixel art)
    // scaler.pixelsPerUnit = 100;
}
```

### Anchors et RectTransform

```text
Anchors: points d'attache du UI element par rapport au parent

7 positions d'ancrage courantes:
- Top-Left:      coins = (0,1, 0,1)  → menus, minimap
- Top-Center:    coins = (0.5,1, 0.5,1) → title
- Top-Right:     coins = (1,1, 1,1)  → score, ammo
- Middle:        coins = (0.5,0.5, 0.5,0.5) → popup, HP bar
- Bottom:        coins = (0,0, 1,0)  → health bar, hotbar
- Stretch:       coins = (0,0, 1,1)  → overlay, fullscreen
- Custom:        coins = (0.2,0.3, 0.8,0.7) → zone spécifique

RectTransform:
- anchoredPosition: position relative aux ancres
- sizeDelta: taille
- offsetMin/offsetMax: décalage par rapport aux ancres
```

### Layout Groups

```csharp
// Horizontal/Vertical Layout Group
// Auto-arrange les enfants horizontalement ou verticalement
// Paramètres:
//   - Spacing: espacement entre éléments
//   - Padding: marges intérieures
//   - Child Alignment: alignement (top, middle, bottom)
//   - Control Child Size: override la taille des enfants
//   - Force Expand: répartir l'espace uniformément

// Grid Layout Group
// Grille régulière (inventaire, hotbar)
// Paramètres:
//   - Cell Size: taille de chaque cellule
//   - Spacing: espacement
//   - Start Corner: où commence la grille
//   - Start Axis: horizontale ou verticale d'abord
//   - Constraint: Fixed Column Count / Fixed Row Count / Flexible

// Content Size Fitter
// Redimensionne automatiquement le conteneur à la taille de son contenu
// UI要素 avec texte dynamique
```

### Unity UI — Optimisation du Canvas

```text
PROBLÈME: chaque modification du Canvas déclenche un rebuild
→ Impact performance si changé chaque frame

RÈGLES:
1. Canvas static = pas de rebuild
2. Pas de layout groups changeant chaque frame
3. Parent = même canvas pour les éléments qui changent ensemble
4. Éviter les Raycast Target inutiles (désactiver sur les images décoratives)
5. Utiliser des Canvas enfants séparés pour les éléments qui changent souvent

Canvas Rebuild Profiler:
- Window → Analysis → Profiler → UI
- Voir le nombre de rebuilds par frame
- Cible: < 5 rebuilds/frame
```

---

## 4. UMG (Unreal Motion Graphics)

### Widget Blueprint Architecture

```text
Widget Blueprint (HealthBar_Widget):
├── Canvas Panel (Root)
│   ├── ProgressBar "HealthBar"
│   │   └── Fill: Image
│   ├── TextBlock "HealthText"
│   └── Image "Background"

Bindings:
- HealthBar.Percent → GetPlayerHealth() / MaxHealth
- HealthText.Text → Format("{0}/{1}", GetPlayerHealth(), GetMaxHealth())
```

### UMG C++

```cpp
// HealthBarWidget.h
UCLASS()
class UHealthBarWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(meta = (BindWidget))
    class UProgressBar* HealthBar;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* HealthText;

    UFUNCTION(BlueprintCallable)
    void SetHealth(float Current, float Max);

    // Animation
    UPROPERTY(Transient, meta = (BindWidgetAnim))
    class UWidgetAnimation* DamageAnimation;
};

// HealthBarWidget.cpp
void UHealthBarWidget::SetHealth(float Current, float Max)
{
    HealthBar->SetPercent(Current / Max);
    HealthText->SetText(FText::FromString(
        FString::Printf(TEXT("%.0f/%.0f"), Current, Max)));

    // Jouer animation si dégâts
    if (Current < PreviousHealth)
        PlayAnimation(DamageAnimation);
    PreviousHealth = Current;
}
```

### Slate (C++ pur, UI Framework d'Unreal)

```cpp
// Slate — UI bas niveau (éditeur, outils)
class SHealthBar : public SCompoundWidget
{
    SLATE_BEGIN_ARGS(SHealthBar)
        : _Percent(1.0f)
    {}
        SLATE_ATTRIBUTE(float, Percent)
        SLATE_ATTRIBUTE(FText, Label)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs)
    {
        ChildSlot
        [
            SNew(SOverlay)
            + SOverlay::Slot()
            [
                SNew(SImage)
                .ColorAndOpacity(FLinearColor::Red)
                .Image(FCoreStyle::Get().GetBrush("WhiteTexture"))
            ]
            + SOverlay::Slot()
            .Padding(2.0f)
            [
                SNew(SImage)
                .ColorAndOpacity(this, &SHealthBar::GetBarColor)
                .Image(FCoreStyle::Get().GetBrush("WhiteTexture"))
                .RenderTransform(this, &SHealthBar::GetBarTransform)
            ]
            + SOverlay::Slot()
            .HAlign(HAlign_Center)
            .VAlign(VAlign_Center)
            [
                SNew(STextBlock)
                .Text(InArgs._Label)
                .Font(FCoreStyle::Get().GetFontStyle("NormalFont"))
            ]
        ];
    }
};
```

---

## 5. Godot Control Nodes

```gdscript
# Godot — HUD Scene
# Control root avec Anchor = Full Rect
extends Control

@onready var health_bar := $VBoxContainer/HealthBar as TextureProgressBar
@onready var health_label := $VBoxContainer/HealthBar/Label as Label
@onready var score_label := $VBoxContainer/ScoreLabel as Label
@onready var inventory_grid := $InventoryGrid as GridContainer

func _ready():
    # Connecter les signaux
    PlayerManager.player_health_changed.connect(_on_health_changed)
    PlayerManager.score_changed.connect(_on_score_changed)

func _on_health_changed(current: float, max: float):
    health_bar.value = current / max * 100.0
    health_label.text = "%d/%d" % [current, max]

    # Animation de dégâts
    var tween = create_tween()
    tween.tween_property(health_bar, "modulate", Color.RED, 0.1)
    tween.tween_property(health_bar, "modulate", Color.WHITE, 0.3)

func _on_score_changed(score: int):
    var tween = create_tween()
    score_label.text = str(score)
    score_label.scale = Vector2(1.2, 1.2)
    tween.tween_property(score_label, "scale", Vector2.ONE, 0.3)

# Godot Theme
# Créer un fichier .tres (Theme) pour centraliser:
# - Default font, font sizes
# - Colors, styles
# - Button styles, Panel styles, Label styles
# Puis assigner au Control root pour propagation
```

### Godot Containers

```gdscript
# Godot container types:
# HBoxContainer   → horizontal
# VBoxContainer   → vertical
# GridContainer   → grille
# CenterContainer → centré
# MarginContainer → marges
# AspectRatioContainer → ratio fixe
# PanelContainer  → avec style

# Exemple: inventaire en grille
func setup_inventory_grid(rows: int, cols: int):
    inventory_grid.columns = cols
    for i in range(rows * cols):
        var slot = preload("res://ui/InventorySlot.tscn").instantiate()
        inventory_grid.add_child(slot)
```

---

## 6. HUD Design — Éléments Clés

### Health Bar — Implémentation Complète

```csharp
public class HealthBar : MonoBehaviour
{
    [SerializeField] private Image _fillImage;
    [SerializeField] private Image _damageImage; // White flash sur dégâts
    [SerializeField] private Image _delayedBar;  // Barre de délai (effet regen)
    [SerializeField] private Text _healthText;

    private float _currentHealth;
    private float _maxHealth;
    private float _displayHealth;    // Pour l'animation smooth
    private float _delayedHealth;    // Suit lentement
    private Coroutine _damageRoutine;

    public void Initialize(float current, float max)
    {
        _currentHealth = current;
        _maxHealth = max;
        _displayHealth = current;
        _delayedHealth = current;
        UpdateDisplay();
    }

    public void SetHealth(float current)
    {
        _currentHealth = current;

        // Animation smooth
        StopAllCoroutines();
        StartCoroutine(AnimateHealth());

        // Flash damage
        if (_damageRoutine != null) StopCoroutine(_damageRoutine);
        _damageRoutine = StartCoroutine(DamageFlash());
    }

    private System.Collections.IEnumerator AnimateHealth()
    {
        // Barre principale suit rapidement
        while (Mathf.Abs(_displayHealth - _currentHealth) > 0.5f)
        {
            _displayHealth = Mathf.Lerp(_displayHealth, _currentHealth, Time.deltaTime * 10f);
            UpdateDisplay();
            yield return null;
        }
        _displayHealth = _currentHealth;
        UpdateDisplay();

        // Barre de délai suit lentement (pour montrer les dégâts reçus)
        if (_currentHealth < _delayedHealth)
        {
            float startDelay = _delayedHealth;
            float elapsed = 0f;
            while (elapsed < 1.5f)
            {
                elapsed += Time.deltaTime;
                _delayedHealth = Mathf.Lerp(startDelay, _currentHealth, elapsed / 1.5f);
                UpdateDelayedBar();
                yield return null;
            }
            _delayedHealth = _currentHealth;
            UpdateDelayedBar();
        }
    }

    private System.Collections.IEnumerator DamageFlash()
    {
        _damageImage.enabled = true;
        _damageImage.color = Color.red;
        yield return new WaitForSeconds(0.1f);
        _damageImage.enabled = false;
    }

    private void UpdateDisplay()
    {
        _fillImage.fillAmount = _displayHealth / _maxHealth;
        _healthText.text = $"{Mathf.RoundToInt(_currentHealth)}/{Mathf.RoundToInt(_maxHealth)}";
    }

    private void UpdateDelayedBar()
    {
        _delayedBar.fillAmount = _delayedHealth / _maxHealth;
    }
}
```

### Crosshair — Système Complet

```csharp
public class Crosshair : MonoBehaviour
{
    [SerializeField] private RectTransform _top, _bottom, _left, _right;
    [SerializeField] private float _baseSpread = 20f;
    [SerializeField] private float _maxSpread = 100f;
    [SerializeField] private float _spreadRecovery = 10f;

    private float _currentSpread;
    private float _targetSpread;

    void Update()
    {
        // Snap to center of screen
        transform.position = new Vector3(Screen.width / 2f, Screen.height / 2f, 0);

        // Spread
        _currentSpread = Mathf.Lerp(_currentSpread, _targetSpread, Time.deltaTime * _spreadRecovery);

        float s = _baseSpread + _currentSpread;
        _top.anchoredPosition = new Vector2(0, s);
        _bottom.anchoredPosition = new Vector2(0, -s);
        _left.anchoredPosition = new Vector2(-s, 0);
        _right.anchoredPosition = new Vector2(s, 0);

        // Recovery
        _targetSpread = Mathf.Lerp(_targetSpread, 0, Time.deltaTime * 2f);
    }

    public void AddSpread(float amount) => _targetSpread += amount;
    public void OnShoot() => AddSpread(10f);
    public void OnMove() => AddSpread(5f);
}
```

### Minimap — Système Complet

```csharp
public class Minimap : MonoBehaviour
{
    [SerializeField] private Camera _minimapCamera;
    [SerializeField] private RectTransform _minimapRect;
    [SerializeField] private GameObject _iconPrefab;
    [SerializeField] private float _worldSize = 500f;
    [SerializeField] private float _iconScale = 1f;

    private Transform _player;
    private Dictionary<Transform, RectTransform> _icons = new();

    void Start()
    {
        _player = GameObject.FindGameObjectWithTag("Player").transform;
        _minimapCamera.transform.SetParent(_player);
        _minimapCamera.transform.localPosition = Vector3.up * 200f;
        _minimapCamera.transform.localRotation = Quaternion.Euler(90, 0, 0);
    }

    public void RegisterIcon(Transform target, Color color, Sprite icon = null)
    {
        var iconObj = Instantiate(_iconPrefab, _minimapRect);
        var iconRect = iconObj.GetComponent<RectTransform>();
        var img = iconObj.GetComponent<Image>();
        img.color = color;
        if (icon) img.sprite = icon;
        _icons[target] = iconRect;
    }

    void LateUpdate()
    {
        // Mettre à jour la position des icônes
        foreach (var kvp in _icons)
        {
            if (kvp.Key == null) continue;

            Vector3 worldPos = kvp.Key.position;
            Vector3 relativePos = worldPos - _player.position;

            // Normaliser dans l'espace de la minimap
            float x = relativePos.x / _worldSize;
            float z = relativePos.z / _worldSize;

            if (Mathf.Abs(x) <= 1 && Mathf.Abs(z) <= 1)
            {
                kvp.Value.gameObject.SetActive(true);
                kvp.Value.anchoredPosition = new Vector2(x * _minimapRect.sizeDelta.x * 0.5f,
                                                         z * _minimapRect.sizeDelta.y * 0.5f);
                kvp.Value.localRotation = Quaternion.Euler(0, 0, -kvp.Key.eulerAngles.y);
            }
            else
            {
                kvp.Value.gameObject.SetActive(false); // Hors zone
            }
        }
    }
}
```

---

## 7. UI Animation

### DOTween (Unity — Recommandé)

```csharp
using DG.Tweening;

public class UIAnimations : MonoBehaviour
{
    public RectTransform panel;
    public Image healthBar;
    public Text damageText;

    void Start()
    {
        // Panel slide-in
        panel.DOAnchorPosY(0, 0.5f).From(new Vector2(0, -100))
             .SetEase(Ease.OutBack);

        // Health bar pulse
        healthBar.DOFillAmount(0.5f, 0.3f)
                 .SetEase(Ease.InOutQuad);

        // Damage number pop
        damageText.DOAnchorPosY(50, 1f).From()
                  .SetEase(Ease.OutQuad);
        damageText.DOFade(0, 1f).From(1);

        // Punch (shake)
        panel.DOPunchPosition(Vector2.right * 10f, 0.3f, 10, 1);

        // Sequence
        Sequence seq = DOTween.Sequence();
        seq.Append(panel.DOScale(0, 0));
        seq.Append(panel.DOScale(1.1f, 0.2f).SetEase(Ease.OutQuad));
        seq.Append(panel.DOScale(1f, 0.1f));
    }
}
```

### LeanTween (Alternative Légère)

```csharp
LeanTween.moveX(panel, 0, 0.5f).setEase(LeanTweenType.easeOutBack);
LeanTween.value(healthBar.gameObject, UpdateFill, 0f, 1f, 0.3f);
LeanTween.alpha(damageText, 0, 1f).setFrom(1);
LeanTween.scale(panel, Vector3.one, 0.3f).setEase(LeanTweenType.easeOutElastic);
```

### Godot Tween

```gdscript
# Godot Tween (intégré)
func show_damage(damage: int):
    var label = preload("res://ui/DamagePopup.tscn").instantiate()
    add_child(label)
    label.text = str(damage)

    var tween = create_tween().set_parallel()
    tween.tween_property(label, "position", label.position + Vector2.UP * 50, 0.8)
    tween.tween_property(label, "modulate", Color.TRANSPARENT, 0.8)
    tween.tween_property(label, "scale", Vector2(1.5, 1.5), 0.2)
```

---

## 8. Inventaire — Drag & Drop

```csharp
public class InventorySlot : MonoBehaviour, IDropHandler, IBeginDragHandler, IDragHandler, IEndDragHandler
{
    [SerializeField] private Image _itemIcon;
    [SerializeField] private Text _stackCount;

    private Item _item;
    private Canvas _canvas;
    private RectTransform _rectTransform;
    private CanvasGroup _canvasGroup;

    void Awake()
    {
        _rectTransform = GetComponent<RectTransform>();
        _canvasGroup = GetComponent<CanvasGroup>();
        _canvas = GetComponentInParent<Canvas>();
    }

    public void SetItem(Item item, int count)
    {
        _item = item;
        _itemIcon.sprite = item.Icon;
        _stackCount.text = count > 1 ? count.ToString() : "";
        _itemIcon.enabled = item != null;
    }

    public void OnBeginDrag(PointerEventData eventData)
    {
        if (_item == null) return;
        _canvasGroup.alpha = 0.6f;
        _canvasGroup.blocksRaycasts = false;
    }

    public void OnDrag(PointerEventData eventData)
    {
        _rectTransform.anchoredPosition += eventData.delta / _canvas.scaleFactor;
    }

    public void OnEndDrag(PointerEventData eventData)
    {
        _canvasGroup.alpha = 1f;
        _canvasGroup.blocksRaycasts = true;
        _rectTransform.anchoredPosition = Vector2.zero;
    }

    public void OnDrop(PointerEventData eventData)
    {
        var otherSlot = eventData.pointerDrag.GetComponent<InventorySlot>();
        if (otherSlot != null)
        {
            InventoryManager.Instance.SwapItems(this, otherSlot);
        }
    }
}
```

---

## 9. Localisation et Accessibilité

### Localisation (String Tables)

```csharp
[CreateAssetMenu(fileName = "StringTable", menuName = "Localization/StringTable")]
public class StringTable : ScriptableObject
{
    [System.Serializable]
    public struct LocalizedString
    {
        public string Key;
        public string English;
        public string French;
        public string German;
        public string Spanish;
        public string Japanese;
        public string Korean;
        public string ChineseSimplified;
    }

    public LocalizedString[] Strings;

    private Dictionary<string, LocalizedString> _lookup;

    public string Get(string key, SystemLanguage language)
    {
        if (_lookup == null)
        {
            _lookup = new Dictionary<string, LocalizedString>();
            foreach (var s in Strings)
                _lookup[s.Key] = s;
        }

        if (!_lookup.TryGetValue(key, out var entry))
            return $"[{key}]"; // Missing key

        return language switch
        {
            SystemLanguage.French => entry.French,
            SystemLanguage.German => entry.German,
            SystemLanguage.Japanese => entry.Japanese,
            SystemLanguage.Korean => entry.Korean,
            SystemLanguage.ChineseSimplified => entry.ChineseSimplified,
            _ => entry.English
        };
    }
}

// Localized text component
public class LocalizedText : MonoBehaviour
{
    [SerializeField] private string _key;
    [SerializeField] private StringTable _table;
    private Text _text;

    void Awake() => _text = GetComponent<Text>();

    void OnEnable() => Refresh();

    public void Refresh()
    {
        if (_text != null)
            _text.text = _table.Get(_key, LocalizationManager.CurrentLanguage);
    }
}
```

### Accessibilité

```csharp
public class AccessibilityOptions : MonoBehaviour
{
    [Header("Text Scaling")]
    [SerializeField] private float _defaultScale = 1f;
    [SerializeField] private float _largeScale = 1.5f;

    [Header("Color Blind")]
    [SerializeField] private Material _deuteranopia;
    [SerializeField] private Material _protanopia;
    [SerializeField] private Material _tritanopia;

    [Header("Audio")]
    [SerializeField] private AudioSource _narrationSource;

    public enum ColorBlindMode { None, Deuteranopia, Protanopia, Tritanopia }

    public void SetTextScale(float scale)
    {
        // Scale tous les Text components
        foreach (var text in Resources.FindObjectsOfTypeAll<Text>())
            text.fontSize = Mathf.RoundToInt(text.fontSize * scale / _defaultScale);
    }

    public void SetColorBlindMode(ColorBlindMode mode)
    {
        // Appliquer le material de correction au camera
        var mat = mode switch
        {
            ColorBlindMode.Deuteranopia => _deuteranopia,
            ColorBlindMode.Protanopia => _protanopia,
            ColorBlindMode.Tritanopia => _tritanopia,
            _ => null
        };
        Camera.main.SetReplacementShader(mat?.shader, "");
    }

    public void SetSubtitles(bool enabled)
    {
        SubtitleManager.Instance.Enabled = enabled;
    }

    public void SetHighContrast(bool enabled)
    {
        var uiCanvas = GameObject.Find("HUD").GetComponent<Canvas>();
        if (enabled)
            uiCanvas.sortingOrder = 999; // Toujours au-dessus
    }
}
```

---

## 10. Pièges Courants

- **Canvas rebuild chaque frame** → UI dynamique qui change de layout à chaque Update. Utiliser un Canvas séparé pour les éléments statiques.
- **Raycast Target sur tout** → Chaque Image/Text a Raycast Target = true → bloque les clics. Désactiver sur les éléments décoratifs.
- **Pas de pool UI** → Instancier/détruire des UI elements (messages de dégâts, notifications) → GC spikes. Pool d'UI elements.
- **Anchors mal configurées** → UI qui sort de l'écran sur 16:9 vs 21:9. Toujours tester avec plusieurs ratios.
- **Pas de Safe Area** → iPhone notch / Dynamic Island qui cache le HUD. Utiliser Screen.safeArea.
- **World Space UI sans billboarding** → UI qui reste dans le sol quand on tourne la tête. Toujours regarder la caméra.
- **Localisation oubliée** → Textes en dur dans le code. Utiliser des string tables partout.
- **Input bloqué par UI** → Cliquer sur un bouton = tir aussi. Utiliser EventSystem.current.IsPointerOverGameObject().
- **Font trop petite** → Illisible sur mobile. Minimum 24px pour le texte principal.
- **Pas de test accessibilité** → Daltoniens, malvoyants, daltoniens ne peuvent pas jouer. Toujours tester.