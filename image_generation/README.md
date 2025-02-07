# FLUX

## Black Forest Labs

![Flux Project Illustration](https://raw.githubusercontent.com/black-forest-labs/flux/main/assets/grid.jpg)

**Sources :**  
- [Hugging Face](https://huggingface.co/black-forest-labs)  
- [GitHub](https://github.com/black-forest-labs/flux)  
- [ML Expert Blog](https://www.mlexpert.io/blog/flux-1-dev)

## Qu'est-ce que FLUX ?

FLUX est un modèle de génération d'images à partir de descriptions textuelles développé par Black Forest Labs, une entreprise allemande spécialisée dans l'intelligence artificielle. Avec 12 milliards de paramètres, FLUX est capable de créer des images de haute qualité en réponse à des invites textuelles.

Il existe en plusieurs versions, dont **FLUX.1 [dev]** et **FLUX.1 [schnell]** :

- **FLUX.1 [schnell]** : Version rapide, sous licence **Apache 2.0**, autorisée pour une utilisation commerciale.  
- **FLUX.1 [dev]** : Version destinée à des applications non commerciales.  
- **FLUX.1 [pro]** : Version professionnelle, disponible uniquement via une API (non disponible dans ce repository).

## Comparaison avec d'autres modèles

Par rapport à d'autres modèles de génération d'images tels que DALL-E 3 et Stable Diffusion XL, FLUX se distingue par sa capacité à générer des images réalistes, notamment des mains humaines, avec une cohérence accrue. Des tests ont montré que les sorties de **FLUX.1 [dev]** et **FLUX.1 [pro]** sont comparables à celles de DALL-E 3 en termes de fidélité aux invites, avec un réalisme photographique similaire à celui de Midjourney 6.

## Configuration de l'authentification Hugging Face

### Objectif

Ce script utilise un fichier `.env` pour stocker de manière sécurisée le token d'accès à Hugging Face. Vous pouvez configurer ce fichier de deux manières : automatiquement avec `huggingface-cli login` ou manuellement.

### Méthode 1 : Configuration automatique avec `huggingface-cli login`

1. Assurez-vous que l'outil `huggingface-cli` est installé (inclus avec `huggingface_hub`). Si besoin, installez-le avec :

   ```bash
   pip install huggingface_hub
   huggingface-cli login
   ```
2. Dans un terminal, exécutez la commande suivante :
   ```bash
   huggingface-cli login
   ```
3. Entrez vos identifiants ou collez un token d'accès généré sur le site Hugging Face. Cela enregistrera automatiquement le token dans le fichier `~/.huggingface/token`. Vous n'avez rien à ajouter dans le fichier `.env`, le script utilisera automatiquement ce token.

### Méthode 2 : Configuration manuelle avec un fichier `.env`
1. Créez un fichier`.env` dans le même dossier que ce script.
2. Ouvrez ce fichier dans un éditeur de texte et ajoutez la ligne suivante :
   ```
   HUGGINGFACE_TOKEN=<votre_token>
   ```

## Dépendances
    ```
    torch
    diffusers
    Pillow
    matplotlib
    tqdm
    python-dotenv
    ```
    
## Code testé avec configuration suivante :
- Carte graphique NVIDIA 16 Go
- Mémoire RAM : 80 Go
- Processeur i7
- Windows 10

## Explication du code

Le code que vous trouvez dans ce dépôt est conçu pour générer LOCALEMENT SUR SON ORDINATEUR des images  à partir de prompts textuels en utilisant le modèle `FLUX` de Black Forest Labs. Ce modèle, disponible via Hugging Face, utilise des techniques avancées de diffusion pour créer des images à partir de descriptions textuelles. 

### Fonctionnalités principales

#### 1. **Authentification Hugging Face**
Le code commence par s'assurer que l'utilisateur est correctement authentifié avec Hugging Face via un token d'authentification. Le token est soit récupéré automatiquement depuis un fichier `.env` (méthode manuelle), soit configuré automatiquement via l'outil `huggingface-cli`. Cela permet d'accéder aux modèles hébergés sur Hugging Face.

#### 2. **Libération de la mémoire GPU**
Avant de commencer à générer des images, le script libère la mémoire GPU en vidant le cache CUDA et en collectant les objets inutilisés avec le garbage collector. Cela permet de s'assurer que suffisamment de mémoire est disponible pour les calculs suivants, particulièrement important lors de l'utilisation de modèles de grande taille.

#### 3. **Choix du modèle FLUX**
Le modèle `FLUX` est chargé via la bibliothèque `diffusers`. Le code offre deux variantes du modèle FLUX :
- `FLUX.1-dev` : Une version de développement, gratuite mais non commerciale.
- `FLUX.1-schnell` : Une version plus rapide et optimisée, disponible sous licence non commerciale.

L'utilisateur peut choisir le modèle qu'il souhaite utiliser, en fonction de ses besoins.

#### 4. **Génération d'images**
La fonction `generate_images` génère des images en utilisant le modèle de diffusion et un texte de prompt donné. L'utilisateur peut spécifier plusieurs paramètres :
- `guidance_scale` : Contrôle l'alignement entre l'image générée et le prompt (plus la valeur est élevée, plus l'image correspondra au prompt).
- `n_steps` : Nombre d'étapes de diffusion utilisées pour générer l'image.
- `lora_scale` : Influence de l'attention jointure pour affiner la génération d'image.
- `n_images` : Nombre d'images à générer.
- `seed` : Permet de reproduire les mêmes résultats en utilisant une valeur de graine.

Les images sont ensuite sauvegardées et affichées sous forme de grille pour que l'utilisateur puisse facilement les visualiser et les comparer.

#### 5. **Exploration avec différentes configurations**
Le code permet de tester plusieurs variantes pour chaque génération d'image :
- **Différents `inference_steps`** : Le nombre d'étapes de diffusion peut être ajusté pour voir comment cela influence la qualité de l'image.
- **Différents `guidance_scale`** : L'échelle de guidance peut être modifiée pour ajuster la fidélité de l'image par rapport au prompt.

Les images générées sont sauvegardées dans des dossiers distincts pour chaque expérimentation afin de garder une trace de toutes les configurations.

1. **Organisation structurée :**
   - Un dossier principal est créé pour chaque session d'exploration, basé sur un horodatage.
   - Ce dossier contient des sous-dossiers spécifiques pour chaque type d'exploration :
     - `exploration_images` : pour les images générées avec différentes seeds.
     - `inference_steps_images` : pour les images générées avec différents nombres d'étapes d'inférence.
     - `guidance_images` : pour les images générées avec différentes échelles d'orientation (guidance scales).

2. **Fichier CSV des métadonnées :**
   - Un fichier CSV est généré dans le dossier principal, incluant les métadonnées pour chaque image générée.
   - Colonnes disponibles :
     - `Time` : Heure de la génération.
     - `Seed` : Seed utilisée pour la génération.
     - `Width` et `Height` : Dimensions de l'image.
     - `Steps` : Nombre d'étapes d'inférence.
     - `Guidance` : Échelle d'orientation utilisée.
     - `LoraScale` : Échelle LoRA appliquée (si pertinent).
     - `Prompt` : Texte du prompt ayant servi à générer l'image.
   - Ce fichier permet de recréer exactement les mêmes images dans des sessions ultérieures.

3. **Sauvegarde des poids intermédiaires (optionnelle) :**
   - Si activée, chaque image est accompagnée d'un fichier contenant les poids (latents) intermédiaires associés. Ces fichiers sont sauvegardés dans le même dossier que l'image et portent le même nom, avec une extension `.pkl`.
   - Ces poids peuvent être utilisés pour explorer les calculs intermédiaires ou régénérer les images sans nécessiter une recalculation complète.

4. **Options de sauvegarde configurables :**
   - Les utilisateurs peuvent activer ou désactiver les fonctionnalités suivantes via des paramètres dans le script :
     - **Sauvegarde des métadonnées** : Par défaut activée.
     - **Sauvegarde des poids intermédiaires** : Désactivée par défaut.

### Conclusion
Ce projet offre une interface simple pour expérimenter avec le modèle FLUX de Black Forest Labs et générer localement sur son ordinateur des images de haute qualité à partir de descriptions textuelles. Il permet une exploration approfondie des différentes configurations du modèle, avec un système de gestion de la mémoire pour maximiser l'efficacité lors de la génération d'images complexes.

## Lancer le notebook
Un lien vers le notebook [image_generation_Flux1.ipynb](image_generation_Flux1.ipynb) permet de générer des images.