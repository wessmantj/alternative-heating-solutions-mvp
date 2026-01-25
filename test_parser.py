from parser import parse_customer_response

# Test 1: Simple format
print("Test 1: Simple format")
msg = """John Smith
123 Main St, Attleboro
Chimney cleaning"""
name, address, service = parse_customer_response(msg)
print(f"Name: {name}")
print(f"Address: {address}")
print(f"Service: {service}")

# Test 2: With labels
print("\nTest 2: With labels")
msg = """Name: Jane Doe
Address: 456 Oak Ave
Service: Chimney repair"""
name, address, service = parse_customer_response(msg)
print(f"Name: {name}")
print(f"Address: {address}")
print(f"Service: {service}")

# Test 3: Mixed format
print("\nTest 3: Mixed")
msg = """Bob Johnson
Address: 789 Elm St
Need chimney inspection"""
name, address, service = parse_customer_response(msg)
print(f"Name: {name}")
print(f"Address: {address}")
print(f"Service: {service}")

# Test 4: Missing info
print("\nTest 4: Missing info")
msg = """Mike Williams
Chimney cleaning"""
name, address, service = parse_customer_response(msg)
print(f"Name: {name}")
print(f"Address: {address}")
print(f"Service: {service}")

print("\n✅ All parser tests complete!")