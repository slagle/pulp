CERT_DIR=./certs
REVOKED_KEY=${CERT_DIR}/revoked_key.pem
REVOKED_CERT=${CERT_DIR}/revoked_cert.pem
REVOKED_CSR=${CERT_DIR}/revoked_csr
CA_CERT=${CERT_DIR}/revoking_ca.pem
CA_KEY=${CERT_DIR}/revoking_ca_key.pem
CA_SERIAL=${CERT_DIR}/revoking_ca_serial
CRL_FILE=${CERT_DIR}/revoking_crl.pem
# INDEX AND CRLNUMBER need to match the setting in the
# openssl conf
INDEX=${CERT_DIR}/index
CRLNUMBER=${CERT_DIR}/crlnumber
CONF_FILE=./revoking_ssl.conf
if [ ! -e ${CERT_DIR} ]; then
    echo "${CERT_DIR} missing, will attempt to create directory"
    mkdir ${CERT_DIR}
fi
#
# Create the CA
#
echo "Creating a test CA"
openssl genrsa -out ${CA_KEY} 2048
openssl req -new -x509 -days 1095 -key ${CA_KEY} -out ${CA_CERT} -subj '/CN=Revoking-CA'
if [ ! -e ${CA_SERIAL} ]; then
    echo "Initializing ${CA_SERIAL}"
    echo "01" > ${CA_SERIAL}
fi
#
# Create a test cert so we can revoke it later
#
echo "Creating a test cert to revoke in later step: ${REVOKED_CERT}"
openssl genrsa -out ${REVOKED_KEY} 2048
openssl req -new -key ${REVOKED_KEY} -out ${REVOKED_CSR} -subj '/CN=Test_Revoked_Cert'
openssl x509 -req -days 1095 -CA ${CA_CERT} -CAkey ${CA_KEY} -in ${REVOKED_CSR} -out ${REVOKED_CERT} -CAserial ${CA_SERIAL}
#
# Setup CRL database info for CRL revoking
#
if [ ! -e ${INDEX} ]; then
    echo "Creating the index"
    touch ${INDEX}
fi
if [ ! -e ${CRLNUMBER} ]; then
    echo "Initializing ${CRLNUMBER}"
    echo "01" > ${CRLNUMBER}
fi
#
# Revoke the cert, then generate a CRL with the newly revoked info
#
echo "Revoking the cert: ${REVOKED_CERT}"
openssl ca -revoke ${REVOKED_CERT} -keyfile ${CA_KEY} -cert ${CA_CERT} -config ${CONF_FILE} -md sha1
openssl ca -gencrl -keyfile ${CA_KEY} -cert ${CA_CERT} -out ${CRL_FILE} -config ${CONF_FILE} -crlexts crl_ext -md sha1