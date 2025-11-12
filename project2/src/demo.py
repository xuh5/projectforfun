from pprint import pprint
from src.acumatica_client import AcumaticaClient, load_config_from_env


def main() -> None:
    """
    Demo: login, fetch first 5 customers, logout.
    Adjust the endpoint/path for your instance/version as needed.
    """
    config = load_config_from_env()
    with AcumaticaClient(config) as client:
        client.login()
        # Common entity name; adjust depending on your installation or customize fields with $expand/$select
        resp = client.get("/entity/Default/6.00.001/Customer", params={"$top": 5})
        data = resp.json()
        pprint(data)


if __name__ == "__main__":
    main()


