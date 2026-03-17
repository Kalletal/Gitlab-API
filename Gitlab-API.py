import yaml
import os
import requests
import logging
from pathlib import Path
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Label, ListView, ListItem, Input, Button, DirectoryTree
from textual.containers import Horizontal, VerticalScroll
from dotenv import load_dotenv
load_dotenv()

CONFIG_FILE = "config.yaml"
GITLAB_URL = os.getenv("GITLAB_URL", "http://localhost")
PROJECT_ID = os.getenv("GITLAB_PROJECT_ID", "1")

logging.basicConfig(
    filename="debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s",
)

def load_config():
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f)
    return None

def save_config(collection_path):
    with open(CONFIG_FILE, "w") as f:
        yaml.dump({"collection_path": collection_path}, f)

def load_collection(filepath):
    with open(filepath, "r") as f:
        return yaml.safe_load(f)

def trigger_pipeline(collection, env_index, variables):
    """Déclenche le pipeline gitlab avec les variables fournies"""

    # Récupérer l'url et le token depuis le fichier de collection
    # request = collection["collection"][0] # A décommenter  en prod
    # url = request["url"] # A décommenter en prod
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/trigger/pipeline"

    logging.debug(f"DEBUG URL : {url}")
    logging.debug(f"DEBUG PROJECT ID : {PROJECT_ID}")
    logging.debug(f"DEBUG GITLAB URL : {GITLAB_URL}")

    # Récupérer le token depuis l'input
    token = variables.pop("token", "")

    logging.debug(f"Token utilisé : {token[:10]}...")

    # Construie les paramètres du POST
    params = {
        "token": token,
        "ref": "main",
    }

    # Ajouter les variables
    for nom, valeur in variables.items():
        params[f"variables[{nom}]"] = valeur

    response = requests.post(url, data=params, verify=False)
    logging.debug(f"Status code : {response.status_code}")
    return response


# --- Ecran de sélection de fichier  ---
class FilePickerScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Sélectionne ton fichier de collection :")
        yield DirectoryTree(Path.home(), id="tree")
        yield Footer()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.dismiss(str(event.path))


# --- Ecran principal
class MainScreen(Screen):

    CSS = """
    #env_list {
        width: 35%;
        height: 100%;
        border: solid green;
    }
    #variables {
        width: 65%;
        height: 100%;
        border: solid blue;
    }
    #btn_deployer {
        dock: bottom;
        margin: 1;
    }
    """

    def __init__(self):
        super().__init__()  # Obligatoire si on surcharge INIT
        self.collection = None   # Initialisation des attributs

    def compose(self) -> ComposeResult:
        config = load_config()
        self.collection = load_collection(config["collection_path"])

        yield Header()

        # Généré avec la liste, depuis le fichier yaml
        # Colonne de gauche : liste des environnements
        environments = self.collection["environments"]["subEnvironments"]
        items = [ListItem(Label(env["name"])) for env in environments]

        # Deux colonnes cote à cote
        with Horizontal():
            yield ListView(*items, id="env_list")
            # Zone des variables - vide au début
            yield VerticalScroll(id="variables")

        yield Button("Déployer", id="btn_deployer", variant="success")
        yield Footer()

    # Cette méthode est appelée automatiquement quand l'utilisateur
    # selectione un élément dans la ListView
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        environments = self.collection["environments"]["subEnvironments"]
        env_selectionne = environments[event.list_view.index]

        # On récupere la zone des variables
        variables_zone = self.query_one("#variables")
        # On efface les anciens champs
        variables_zone.remove_children()

        # On récupere un champs Input pour chaque variables
        for nom, valeur in env_selectionne["data"].items():
            variables_zone.mount(Label(f"{nom} :"))
            variables_zone.mount(Input(value=str(valeur), placeholder=nom))

        self.notify(f"Environnement sélectionné : {env_selectionne['name']}", timeout=4.0)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_deployer":
            # Récuperer toutes les valeurs des Input
            variables = {}
            for input_widget in self.query_one("#variables").query(Input):
                variables[input_widget.placeholder] = input_widget.value

            self.notify(f"Déploiement : {variables}")

            # Récupérer l'index de l'environnement selectionné
            env_index = self.query_one("#env_list").index

            # Déclencher les pipeline
            try:
                response = trigger_pipeline(self.collection, env_index, variables)
                if response.status_code == 201:
                    self.notify("Pipeline déclenché !", title="✅ Succès", severity="information")
                else:
                    self.notify(f"Erreur : {response.status_code}", title="❌ Erreur", severity="error")
            except Exception as exc:
                self.notify(str(exc), title="❌ Erreur", severity="error")


# --- Application principale ---
class gitlabapi(App):

    BINDINGS = [("c", "config", "Config")]

    def on_mount(self) -> None:
        config = load_config()
        if config and os.path.isfile(config.get("collection_path", "")):
            self.call_after_refresh(self.push_screen, MainScreen())
        else:
            self.call_after_refresh(self.push_screen, FilePickerScreen(), self.collection_chargee())

    def collection_chargee(self, path) -> None:
        if path and os.path.isfile(path):
            save_config(path)
            self.notify("Collection chargée !", severity="information")
            self.call_after_refresh(self.push_screen, MainScreen())
        else:
            self.notify("Fichier invalide !", severity="error")

    def action_config(self) -> None:
        self.push_screen(FilePickerScreen(), callback=self.collection_chargee)


if __name__ == "__main__":
    app = gitlabapi()
    app.run()
