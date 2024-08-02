from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Rota para a página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        token = request.form['token']
        session['api_key'] = token
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('login.html')

# Configuração inicial
base_url = 'https://www.asaas.com/api/v3'  # Production URL

# Função para atualizar valor de assinatura
def update_subscription(subscription_id, new_value, api_key):
    url = f'{base_url}/subscriptions/{subscription_id}'
    headers = {
        'Content-Type': 'application/json',
        'access_token': api_key
    }
    data = {
        'value': new_value
    }
    response = requests.put(url, headers=headers, json=data)
    return response.json(), response.status_code

# Função para enviar alerta de cobrança
def send_payment_reminder(customer_id, due_date, value, api_key):
    url = f'{base_url}/payments'
    headers = {
        'Content-Type': 'application/json',
        'access_token': api_key
    }
    data = {
        'customer': customer_id,
        'dueDate': due_date,
        'value': value,
        'billingType': 'BOLETO',  # ou 'CREDIT_CARD', 'PIX'
        'description': 'Mensalidade em atraso'
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json(), response.status_code

# Função para buscar todas as assinaturas
def get_all_subscriptions(api_key):
    url = f'{base_url}/subscriptions'
    headers = {
        'access_token': api_key
    }
    response = requests.get(url, headers=headers)
    
    try:
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        subscriptions = response.json()
        if response.status_code == 200:
            for subscription in subscriptions.get('data', []):
                customer_id = subscription.get('customer')
                customer_details, _ = get_customer_details(customer_id, api_key)
                subscription['customer_name'] = customer_details.get('name', 'Nome não disponível')
        return subscriptions, response.status_code
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Print the HTTP error
    except requests.exceptions.RequestException as err:
        print(f'Error occurred: {err}')  # Print any other error
    except ValueError:
        print('Invalid JSON received')
    
    return {}, response.status_code

def get_customer_details(customer_id, api_key):
    url = f'{base_url}/customers/{customer_id}'
    headers = {
        'access_token': api_key
    }
    response = requests.get(url, headers=headers)
    
    try:
        response.raise_for_status()
        return response.json(), response.status_code
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Error occurred: {err}')
    except ValueError:
        print('Invalid JSON received')
    
    return {}, response.status_code

@app.route('/')
def index():
    if 'api_key' not in session:
        return redirect(url_for('login'))
    
    api_key = session['api_key']
    subscriptions, status = get_all_subscriptions(api_key)
    if status != 200:
        flash('Erro ao buscar assinaturas. Verifique a chave da API e tente novamente.', 'danger')
    return render_template('index.html', subscriptions=subscriptions.get('data', []))

@app.route('/update_subscription', methods=['POST'])
def update_sub():
    if 'api_key' not in session:
        return redirect(url_for('login'))

    api_key = session['api_key']
    subscription_id = request.form['subscription_id']
    new_value = float(request.form['new_value'])
    update_type = request.form['update_type']

    # Obter valor atual da assinatura
    subscriptions, status = get_all_subscriptions(api_key)
    current_value = None
    for subscription in subscriptions.get('data', []):
        if subscription['id'] == subscription_id:
            current_value = subscription['value']
            break

    if current_value is not None:
        if update_type == 'increase':
            new_value = current_value + new_value
        elif update_type == 'decrease':
            new_value = current_value - new_value

        response, status = update_subscription(subscription_id, new_value, api_key)
        if status == 200:
            flash('Assinatura atualizada com sucesso!', 'success')
        else:
            flash('Erro ao atualizar assinatura.', 'danger')
    else:
        flash('Assinatura não encontrada.', 'danger')

    return redirect(url_for('index'))

@app.route('/send_reminder', methods=['POST'])
def send_reminder():
    if 'api_key' not in session:
        return redirect(url_for('login'))

    api_key = session['api_key']
    customer_id = request.form['customer_id']
    due_date = request.form['due_date']
    value = float(request.form['value'])
    response, status = send_payment_reminder(customer_id, due_date, value, api_key)
    if status == 200:
        flash('Alerta enviado com sucesso!', 'success')
    else:
        flash('Erro ao enviar alerta.', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
