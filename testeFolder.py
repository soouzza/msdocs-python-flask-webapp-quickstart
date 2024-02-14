from flask import Flask, request, render_template_string
import base64
from PIL import Image
import io
import requests
import json
import aiohttp
import asyncio

# from flask_asyncio import async_setup

app = Flask(__name__)
# async_setup(app)
#server = app.server

HTML = """
<!doctype html>
<html>
<head>
    <title>MVP Supermercados</title>
</head>
<body>
    <h1>Enviar imagem</h1>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="image">
        <input type="submit" value="Enviar">
    </form>
    {% if items %}
        </br></br><h2>Itens Disponíveis no {{ supermercado }}</h2>
        <p>Validade: {{ validade }}</p>
        <table border="1">
            <tr>
                <th>ID</th>
                <th>Nome</th>
                <th>Preço</th>
            </tr>
            {% for item in items %}
            <tr>
                <td>{{ item.id }}</td>
                <td>{{ item.nome }}</td>
                <td>R$ {{ item.preco }}</td>
            </tr>
            {% endfor %}
        </table>
    {% endif %}
</body>
</html>
"""

API_URL = "https://hefestostatum-dev.azurewebsites.net/api/TriggerHermes?code=B9kFj1fHqVJ9j2aQ3n90ZaEKnDT7u20Dsubk_5mEue47AzFu_hORJw=="


def clean_json_string(content):
    cleaned_content = content.replace("\n", "")
    cleaned_content = cleaned_content.replace("`", "")
    cleaned_content = cleaned_content.replace("json", "")
    cleaned_content = cleaned_content.replace(".", ",")
    return cleaned_content


@app.route("/", methods=["GET", "POST"])
async def upload_image():
    response_data = None
    if request.method == "POST":
        file = request.files.get("image")
        if file:
            image_bytes = file.read()
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            From = "souza"
            Prompt = "A imagem é um encarte ou folheto de um Supermercado, mostrando as promoções do dia. Me retorne apenas uma tabela em formato JSON, com as informações do supermercado, data de validade e duas colunas, a primeira coluna com o nome do produto e a segunda coluna com o preço desse produto. Seja preciso, apenas inclua produtos e preços que tenha certeza quanto a estar correto na leitura do encarte. Se você conseguir encontrar a informação de qual é a empresa ou supermercado, inclua no campo 'supermercado', se encontrar alguma informação sobre validade dos valores dos produtos, inclua no campo 'validade', apenas informe esses dados se tiver certeza da informação. Não inclua nenhuma explicação, forneça apenas uma resposta JSON compatível com RFC8259 seguindo este formato sem desvios: {'supermercado':'Novo Mundo', 'validade':'válido até 10/01/2024', 'items': [ { 'id': 1, 'nome': 'Arroz', 'preco': 10,30 }, { 'id': 2, 'nome': 'Feijão', 'preco': 21,10 }, { 'id': 3, 'nome': 'Café', 'preco': 9,10 } ] }"

            async with aiohttp.ClientSession() as session:
                payload = {"From": From, "Prompt": Prompt, "Imagem": image_base64}
                async with session.post(API_URL, json=payload) as response:
                    if response.status == 200:
                        # json_response = await response.json()
                        # content_value = json_response['choices'][0]['message']['content']
                        # cleaned_content = clean_json_string(content_value)
                        # response_data = cleaned_content
                        response_data = await response.text()
                        cleaned_content = clean_json_string(response_data)
                        data = json.loads(
                            cleaned_content
                        )  # Deserializa o JSON para um objeto Python
                        content_value = data["choices"][0]["message"]["content"]
                        cleaned_content = clean_json_string(content_value)
                        data = json.loads(cleaned_content)
                        return render_template_string(
                            HTML,
                            supermercado=data["supermercado"],
                            validade=data["validade"],
                            items=data["items"],
                        )

                    else:
                        # response_data = f'Erro ao enviar imagem para a API. Código de status: {response.status}'
                        return render_template_string(
                            HTML,
                            error=f"Erro ao enviar imagem para a API. Código de status: {response.status}",
                        )

        else:
            # response_data = 'Nenhum arquivo foi selecionado.'
            return render_template_string(HTML, error="Nenhum arquivo foi selecionado.")

    # return render_template_string(HTML, response=response_data)
    return render_template_string(HTML)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
