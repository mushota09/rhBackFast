"""Script de vérification finale de la syntaxe"""
import py_compile
import sys
from pathlib import Path

files_to_check = [
    "app/core/config.py",
    "app/core/database.py",
    "app/core/security.py",
    "app/user_app/models.py",
    "app/user_app/schemas.py",
    "app/user_app/routes.py",
    "app/paie_app/models.py",
    "app/paie_app/schemas.py",
    "app/paie_app/routes.py",
    "main.py",
]

print("=" * 80)
print("VÉRIFICATION SYNTAXE - FASTAPI VIEWS")
print("=" * 80)

all_ok = True
errors = []

for file_path in files_to_check:
    try:
        py_compile.compile(file_path, doraise=True)
        print(f"✅ {file_path}")
    except py_compile.PyCompileError as e:
        print(f"❌ {file_path}")
        print(f"   Erreur: {e}")
        errors.append((file_path, str(e)))
        all_ok = False
    except FileNotFoundError:
        print(f"⚠️  {file_path} - Fichier non trouvé")
        errors.append((file_path, "Fichier non trouvé"))
        all_ok = False

print("\n" + "=" * 80)
print("RÉSUMÉ")
print("=" * 80)

if all_ok:
    print("\n✅ TOUS LES FICHIERS SONT VALIDES!")
    print(f"   {len(files_to_check)} fichiers vérifiés")
    sys.exit(0)
else:
    print(f"\n❌ {len(errors)} ERREUR(S) DÉTECTÉE(S):")
    for file_path, error in errors:
        print(f"   - {file_path}: {error}")
    sys.exit(1)
