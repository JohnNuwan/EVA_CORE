---
name: shaders-programming
description: Guide complet de programmation de shaders — HLSL, GLSL, GLSL ES (Godot), ShaderGraph, compute shaders, post-processing, VFX, optimisation GPU. Couvre Unity URP/HDRP, Unreal Engine 5, et Godot 4.
---

# Shaders Programming — Guide Complet

Ce skill couvre la programmation de shaders pour le jeu vidéo : vertex, fragment, compute, et post-process. À charger pour toute tâche impliquant des shaders HLSL/GLSL, ShaderGraph, ou optimisation GPU.

---

## 1. Pipeline Graphique Moderne (Rendu)

```
CPU → Draw Call → Vertex Shader → Tessellation → Geometry Shader → Rasterization → Fragment Shader → Output Merger → Framebuffer
                                                      ↓
                                              Compute Shader (indépendant)
```

| Shader | Rôle | Fréquence | Limite |
|--------|------|-----------|--------|
| **Vertex** | Transforme les sommets (position, normal, UV) | Par sommet | ~1000 instructions |
| **Fragment/Pixel** | Calcule la couleur de chaque pixel | Par pixel | ~10000 instructions |
| **Compute** | Calcul généraliste (particules, post-process) | Par thread | ~100000 instructions |
| **Tessellation** | Subdivise les polygones | Par patch | Courbe de détail |

---

## 2. HLSL (Unity / Unreal Engine)

### Vertex + Fragment Shader de base (Unity)

```hlsl
Shader "Custom/ToonLit"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
        _Color ("Couleur", Color) = (1,1,1,1)
        _Ramp ("Ramp Lighting", 2D) = "white" {}
        _Outline ("Outline Width", Range(0,0.1)) = 0.02
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }
        
        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 worldNormal : TEXCOORD0;
                float2 uv : TEXCOORD1;
                float3 worldPos : TEXCOORD2;
            };

            TEXTURE2D(_MainTex); SAMPLER(sampler_MainTex);
            TEXTURE2D(_Ramp); SAMPLER(sampler_Ramp);
            float4 _MainTex_ST;
            float4 _Color;

            Varyings vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.worldNormal = TransformObjectToWorldNormal(input.normalOS);
                output.uv = TRANSFORM_TEX(input.uv, _MainTex);
                output.worldPos = TransformObjectToWorld(input.positionOS.xyz);
                return output;
            }

            float4 frag(Varyings input) : SV_Target
            {
                // Toon lighting
                float3 normal = normalize(input.worldNormal);
                Light mainLight = GetMainLight();
                float NdotL = dot(normal, mainLight.direction) * 0.5 + 0.5;
                
                // Ramp shading (bandes discrètes)
                float ramp = SAMPLE_TEXTURE2D(_Ramp, sampler_Ramp, float2(NdotL, 0)).r;
                
                // Texture
                float4 tex = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, input.uv);
                float3 diffuse = tex.rgb * _Color.rgb * ramp * mainLight.color;
                float3 ambient = SampleSH(normal) * tex.rgb * 0.3;
                
                return float4(diffuse + ambient, 1);
            }
            ENDHLSL
        }
    }
}
```

### Outline Shader (Unreal HLSL)

```hlsl
// Unreal Material Expression (custom node)
// In: UV, Color, Normals → Out: Emissive

float3 ViewPos = mul(GetWorldToView(), float4(GetWorldPosition(Parameters), 1)).xyz;
float3 ViewNormal = mul(GetWorldToView(), float4(GetWorldNormal(Parameters), 0)).xyz;
float Fresnel = 1.0 - abs(dot(normalize(ViewPos), ViewNormal));
return lerp(0, 1, pow(Fresnel, 2.0)) * float3(0, 0, 0); // Black outline
```

---

## 3. GLSL (OpenGL / Godot)

### Shader Canvas 2D (Godot)

```glsl
shader_type canvas_item;

// --- Effet Pixelate ---
uniform float pixel_size : hint_range(1, 100) = 16.0;

void fragment() {
    vec2 uv = UV;
    vec2 size = 1.0 / pixel_size;
    uv = floor(uv / size) * size;
    COLOR = texture(TEXTURE, uv);
}

// --- Effet Dissolve ---
uniform float dissolve_amount : hint_range(0.0, 1.0) = 0.5;
uniform sampler2D noise_texture : hint_white;

void fragment() {
    vec4 tex = texture(TEXTURE, UV);
    float noise = texture(noise_texture, UV).r;
    float cutoff = dissolve_amount;
    
    if (noise < cutoff) discard;
    
    // Edge glow
    float edge = smoothstep(cutoff - 0.1, cutoff, noise);
    COLOR = mix(tex, vec4(1.0, 0.5, 0.0, 1.0), edge * (1.0 - step(0.99, dissolve_amount)));
}
```

### Shader 3D Spatial (Godot)

```glsl
shader_type spatial;
render_mode unshaded, depth_draw_opaque;

uniform float wave_strength : hint_range(0.0, 2.0) = 0.5;
uniform float wave_speed : hint_range(0.0, 5.0) = 1.0;

void vertex() {
    // Wave vertex displacement
    vec3 pos = VERTEX;
    float wave = sin(pos.x * 2.0 + TIME * wave_speed) * wave_strength;
    wave += cos(pos.z * 3.0 + TIME * 0.8) * wave_strength * 0.5;
    pos.y += wave;
    VERTEX = pos;
}

void fragment() {
    ALBEDO = vec3(0.1, 0.4, 0.8);
    METALLIC = 0.3;
    ROUGHNESS = 0.2;
    // Fake foam
    float foam = sin(UV.x * 50.0 + TIME * 2.0) * 0.5 + 0.5;
    ALBEDO = mix(ALBEDO, vec3(1.0), foam * 0.1);
}
```

---

## 4. Compute Shaders (GPU General Purpose)

### Compute Shader Unity (HLSL)

```hlsl
// ComputeShader.compute
#pragma kernel ParticuleUpdate

struct Particule
{
    float3 position;
    float3 velocity;
    float life;
};

RWStructuredBuffer<Particule> particules;
float deltaTime;
float3 attractor;

[numthreads(64, 1, 1)]
void ParticuleUpdate(uint3 id : SV_DispatchThreadID)
{
    uint i = id.x;
    Particule p = particules[i];
    
    // Gravity toward attractor
    float3 dir = attractor - p.position;
    float dist = length(dir);
    p.velocity += normalize(dir) * (1.0 / max(dist, 0.1)) * deltaTime * 10.0;
    
    // Damping
    p.velocity *= 0.99;
    p.position += p.velocity * deltaTime;
    
    // Life
    p.life -= deltaTime;
    if (p.life <= 0)
    {
        p.position = attractor + (float3(rand(i), rand(i+1), rand(i+2)) - 0.5) * 10.0;
        p.velocity = 0;
        p.life = 2.0;
    }
    
    particules[i] = p;
}
```

### Appel C# du Compute Shader

```csharp
public class ParticuleManager : MonoBehaviour
{
    public ComputeShader computeShader;
    public int count = 10000;
    
    private ComputeBuffer _buffer;
    private int _kernel;

    void Start()
    {
        _kernel = computeShader.FindKernel("ParticuleUpdate");
        _buffer = new ComputeBuffer(count, sizeof(float) * 7); // 3+3+1 floats
        computeShader.SetBuffer(_kernel, "particules", _buffer);
        computeShader.SetFloat("deltaTime", Time.deltaTime);
        computeShader.Dispatch(_kernel, Mathf.CeilToInt(count / 64f), 1, 1);
    }
}
```

---

## 5. Post-Processing Shaders

### Post-Process — Bloom (HLSL)

```hlsl
// Fragment shader pour bloom
// Étape 1: Extraire les zones lumineuses
float4 BrightPass(Varyings input) : SV_Target
{
    float4 color = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, input.uv);
    float luminance = dot(color.rgb, float3(0.299, 0.587, 0.114));
    float threshold = 0.8;
    float4 bright = max(0, color - threshold);
    return bright * luminance;
}

// Étape 2: Blur Gaussien (horizontal)
float4 BlurH(Varyings input) : SV_Target
{
    float2 offset = float2(_BlurSize / _ScreenParams.x, 0);
    float4 result = 0;
    float weights[5] = {0.227, 0.194, 0.122, 0.055, 0.015};
    for (int i = -4; i <= 4; i++)
    {
        result += SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, input.uv + offset * i) * weights[abs(i)];
    }
    return result;
}

// Étape 3: Composite
float4 Composite(Varyings input) : SV_Target
{
    float4 base = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, input.uv);
    float4 bloom = SAMPLE_TEXTURE2D(_BloomTex, sampler_BloomTex, input.uv);
    return base + bloom * _Intensity;
}
```

### Post-Process — Watercolor (Godot GLSL)

```glsl
shader_type canvas_item;

uniform float brush_size : hint_range(1, 20) = 4.0;
uniform float paper_grain : hint_range(0.0, 0.5) = 0.2;

void fragment() {
    vec2 uv = UV;
    vec4 color = vec4(0.0);
    
    // Multi-sample watercolor effect
    for (int x = -2; x <= 2; x++) {
        for (int y = -2; y <= 2; y++) {
            vec2 offset = vec2(x, y) * brush_size / TEXTURE_PIXEL_SIZE;
            float dist = length(vec2(x, y)) / 2.0;
            float weight = 1.0 / (1.0 + dist * dist);
            color += texture(TEXTURE, uv + offset) * weight;
        }
    }
    color /= 25.0; // normalize
    
    // Paper grain noise
    float grain = hash(uv * 100.0) * paper_grain;
    COLOR = color + vec4(grain, grain, grain, 0);
}
```

---

## 6. Shader Graph (Unity / Unreal)

### Noeuds essentiels ShaderGraph
```
Groupe               | Noeuds
PBR de base          | PBR Master, Albedo, Metallic, Smoothness, Normal
Math                 | Add, Multiply, Lerp, Saturate, Remap, Smoothstep
UV                   | Tiling And Offset, Polar Coordinates, Rotate
Procedural           | Noise (Gradient/Simple/Voronoi), Gradient Noise
Lighting             | Main Light Direction, NDotL, Half Vector
Utility              | Fresnel Effect, Screen Position, Scene Color
Channel              | Split, Combine, Swizzle
Time                 | Time, Sine Time, Cosine Time
```

### Master Stack URP (Unity)
```
Vertex → Position → Normal → Tangent → UV0
Fragment → Base Color → Normal → Metallic → Smoothness → Occlusion → Emission → Alpha
```

---

## 7. Optimisation GPU

### Règles de performance shader

```
# Priorité d'optimisation
1. Réduire les calculs de gros flottants (pow, exp, sin/cos)
2. Éviter les branches divergentes (if/else dans les warps)
3. Minimiser les textures samples (bindless texture arrays)
4. Utiliser des half/mediump quand la précision n'est pas critique
5. Éviter les boucles dynamiques (runtime-variable iterations)

# Coût relatif des opérations
Addition       : 1 cycle
Multiplication : 1 cycle
Multiply-Add   : 1 cycle (FMA)
Texture Sample : 10-50 cycles (dépend du cache)
Pow/Exp/Log    : 10-20 cycles
Sin/Cos        : 10-15 cycles
Division       : 5-10 cycles
sqrt           : 5-10 cycles
```

### Profiling GPU
```bash
# Unity: Window → Analysis → Frame Debugger
# Unreal: stat gpu, ProfileGPU
# Godot: Debugger → Monitors → GPU
# RenderDoc: Capture frame (tous moteurs)

# Key metrics:
# - Draw calls: < 500 (mobile), < 2000 (PC)
# - Triangles: < 100k (mobile), < 2M (PC)
# - Overdraw: < 3x (fillrate limit)
# - Texture samples: < 20 par fragment
```

---

## 8. Techniques Avancées

### Screen Space Reflections (SSR)
```hlsl
// Ray-march dans l'espace écran
float4 SSR(float3 position, float3 direction)
{
    float3 ray = position;
    for (int i = 0; i < 32; i++)
    {
        ray += direction * 0.1;
        float4 screenPos = mul(ProjectionMatrix, float4(ray, 1));
        screenPos.xy /= screenPos.w;
        float depth = tex2D(_CameraDepthTexture, screenPos.xy).r;
        if (abs(ray.z - depth) < 0.01)
            return tex2D(_MainTex, screenPos.xy);
    }
    return 0;
}
```

### Parallax Occlusion Mapping
```hlsl
// POM: relief mapping avec occlusion
float2 ParallaxOcclusion(float2 uv, float3 viewDir, float heightScale)
{
    float layers = lerp(8, 32, abs(dot(float3(0,0,1), viewDir)));
    float layerDepth = 1.0 / layers;
    float currentDepth = 0.0;
    float2 deltaUV = viewDir.xy * heightScale / layers;
    float2 currentUV = uv;
    float height = 1 - tex2D(_HeightMap, currentUV).r;
    
    while (currentDepth < height)
    {
        currentUV -= deltaUV;
        height = 1 - tex2D(_HeightMap, currentUV).r;
        currentDepth += layerDepth;
    }
    return currentUV;
}
```

---

## 9. Pièges Courants

- **Branching dans les shaders** : les warps GPU exécutent les DEUX branches → préférer lerp/step
- **Précision flottante** : mediump (half) OK pour couleurs, pas pour positions monde
- **Texture samples dans les boucles** : coût exponentiel, préférer des textures pré-calculées
- **Shader compilation stutter** : compiler au chargement, pas en runtime (async compilation)
- **Compute buffers trop grands** : max 64MB sur mobile, 256MB+ sur PC
- **Transparent sorting** : les matériaux transparents ne s'écrivent pas dans le depth buffer
- **Manque de SRP batcher** : Unity URP/HDRP nécessite des matériaux qui partagent le même shader