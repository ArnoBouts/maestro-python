## Install

```
docker volume create maestro
```

```
docker run --rm -e MAESTRO_DOMAIN=no-cloud.fr -e LDAP_ADMIN_PASSWORD=secretpassword -v maestro:/maestro/services -v /var/run/docker.sock:/var/run/docker.sock no-cloud.fr/maestro-python --install
```
