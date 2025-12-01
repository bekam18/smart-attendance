"""Test if routes are registered"""
from app import create_app

app = create_app()

print("\n" + "="*60)
print("REGISTERED ROUTES")
print("="*60)

for rule in app.url_map.iter_rules():
    if 'attendance' in str(rule):
        print(f"{rule.methods} {rule}")

print("="*60)
