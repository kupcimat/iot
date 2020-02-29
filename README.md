# iot
To run the `webthings-server.py`, you first need to create a `webthings-mapping.yaml` configuration file.

### Example Configuration file
```yaml
webthings:
  - temperature-sensor:
      id: "urn:test:ro:temperature"
      title: "Test temperature"
      description: "Test temperature"
      provider: random-value-generator
      update-interval: 60
```
