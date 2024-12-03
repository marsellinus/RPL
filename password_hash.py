from werkzeug.security import generate_password_hash

# Masukkan password yang ingin di-hash
password = input("Masukkan password yang ingin di-hash: ")

# Generate hash password
hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

# Print hasil hash
print("Password hash:", hashed_password)