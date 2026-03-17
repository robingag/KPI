"""Generate self-signed certificate for HTTPS server."""
import subprocess
import sys
import os

certfile = os.path.join(os.path.dirname(__file__), "cert.pem")
keyfile = os.path.join(os.path.dirname(__file__), "key.pem")

# Use Python's ssl module approach - generate with openssl command if available
# Otherwise use a pure-python approach
try:
    # Try openssl command
    subprocess.run([
        "openssl", "req", "-x509", "-newkey", "rsa:2048",
        "-keyout", keyfile, "-out", certfile,
        "-days", "365", "-nodes",
        "-subj", "/CN=192.168.0.221",
        "-addext", "subjectAltName=IP:192.168.0.221,IP:127.0.0.1,DNS:localhost"
    ], check=True, capture_output=True)
    print(f"Certificate generated: {certfile}")
    print(f"Key generated: {keyfile}")
except FileNotFoundError:
    print("openssl not found, trying with Python cryptography...")
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime, ipaddress

        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "192.168.0.221"),
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.IPAddress(ipaddress.IPv4Address("192.168.0.221")),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                    x509.DNSName("localhost"),
                ]),
                critical=False,
            )
            .sign(key, hashes.SHA256())
        )

        with open(keyfile, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))

        with open(certfile, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        print(f"Certificate generated: {certfile}")
        print(f"Key generated: {keyfile}")
    except ImportError:
        print("ERROR: Neither openssl nor cryptography library available.")
        print("Install with: pip install cryptography")
        sys.exit(1)
