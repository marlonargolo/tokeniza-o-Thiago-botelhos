from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import json
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'

base_url = 'https://www.asaas.com/api/v3'

# Configura o logging
logging.basicConfig(level=logging.DEBUG)

# Função para atualizar valor de assinatura com logging
def update_subscription(subscription_id, new_value, new_date, api_key):
    url = f'{base_url}/subscriptions/{subscription_id}'
    headers = {
        'Content-Type': 'application/json',
        'access_token': api_key
    }
    data = {
        'value': new_value,
        'date': new_date
    }
    
    # Log do JSON que está sendo enviado
    logging.debug(f'Sending JSON to {url}: {json.dumps(data)}')
    
    response = requests.put(url, headers=headers, json=data)
    try:
        response.raise_for_status()
        logging.debug(f'Successfully updated subscription: {response.json()}')
        return response.json(), response.status_code
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err} - {response.text}')
    except requests.exceptions.RequestException as err:
        logging.error(f'Error occurred: {err}')
    except ValueError:
        logging.error('Invalid JSON received')
    return {}, response.status_code

# Função para enviar alerta de cobrança com logging
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
        'billingType': 'BOLETO',
        'description': 'Mensalidade em atraso'
    }

    # Log do JSON que está sendo enviado
    logging.debug(f'Sending JSON to {url}: {json.dumps(data)}')
    
    response = requests.post(url, headers=headers, json=data)
    try:
        response.raise_for_status()
        logging.debug(f'Successfully sent payment reminder: {response.json()}')
        return response.json(), response.status_code
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err} - {response.text}')
    except requests.exceptions.RequestException as err:
        logging.error(f'Error occurred: {err}')
    except ValueError:
        logging.error('Invalid JSON received')
    return {}, response.status_code

# Função para obter todas as assinaturas com logging
def get_all_subscriptions(api_key):
    url = f'{base_url}/subscriptions'
    headers = {'access_token': api_key}
    response = requests.get(url, headers=headers)
    
    try:
        response.raise_for_status()
        subscriptions = response.json()
        logging.debug(f'Subscriptions received: {subscriptions}')
        if response.status_code == 200:
            for subscription in subscriptions.get('data', []):
                customer_id = subscription.get('customer')
                customer_details, _ = get_customer_details(customer_id, api_key)
                subscription['customer_name'] = customer_details.get('name', 'Nome não disponível')
        return subscriptions, response.status_code
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err} - {response.text}')
    except requests.exceptions.RequestException as err:
        logging.error(f'Error occurred: {err}')
    except ValueError:
        logging.error('Invalid JSON received')
    
    return {}, response.status_code

# Função para obter detalhes do cliente com logging
def get_customer_details(customer_id, api_key):
    url = f'{base_url}/customers/{customer_id}'
    headers = {'access_token': api_key}
    response = requests.get(url, headers=headers)
    
    try:
        response.raise_for_status()
        logging.debug(f'Customer details received: {response.json()}')
        return response.json(), response.status_code
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err} - {response.text}')
    except requests.exceptions.RequestException as err:
        logging.error(f'Error occurred: {err}')
    except ValueError:
        logging.error('Invalid JSON received')
    
    return {}, response.status_code

# Função para obter todos os pagamentos de um cliente com logging
def get_customer_payments(customer_id, api_key):
    url = f'{base_url}/payments'
    headers = {'access_token': api_key}
    params = {'customer': customer_id}
    response = requests.get(url, headers=headers, params=params)
    
    try:
        response.raise_for_status()
        logging.debug(f'Customer payments received: {response.json()}')
        return response.json(), response.status_code
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err} - {response.text}')
    except requests.exceptions.RequestException as err:
        logging.error(f'Error occurred: {err}')
    except ValueError:
        logging.error('Invalid JSON received')
    
    return {}, response.status_code

# Função para atualizar a data de vencimento do pagamento com logging
def update_due_date(payment_id, new_due_date, api_key):
    url = f'{base_url}/payments/{payment_id}'
    headers = {
        'Content-Type': 'application/json',
        'access_token': api_key
    }
    data = {'dueDate': new_due_date}
    
    # Log do JSON que está sendo enviado
    logging.debug(f'Sending JSON to {url}: {json.dumps(data)}')
    
    response = requests.put(url, headers=headers, json=data)
    try:
        response.raise_for_status()
        logging.debug(f'Successfully updated due date: {response.json()}')
        return response.json(), response.status_code
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err} - {response.text}')
    except requests.exceptions.RequestException as err:
        logging.error(f'Error occurred: {err}')
    except ValueError:
        logging.error('Invalid JSON received')
    return {}, response.status_code

# Função para atualizar a data da mensalidade com logging
def update_subscription_due_date(subscription_id, new_due_date, api_key):
    url = f'{base_url}/subscriptions/{subscription_id}'
    headers = {
        'Content-Type': 'application/json',
        'access_token': api_key
    }
    data = {'dueDate': new_due_date}
    
    # Log do JSON que está sendo enviado
    logging.debug(f'Sending JSON to {url}: {json.dumps(data)}')
    
    response = requests.put(url, headers=headers, json=data)
    try:
        response.raise_for_status()
        logging.debug(f'Successfully updated subscription due date: {response.json()}')
        return response.json(), response.status_code
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err} - {response.text}')
    except requests.exceptions.RequestException as err:
        logging.error(f'Error occurred: {err}')
    except ValueError:
        logging.error('Invalid JSON received')
    return {}, response.status_code

# Função para debitar a próxima cobrança com logging
def debit_next_charge(subscription_id, api_key):
    url = f'{base_url}/subscriptions/{subscription_id}/debit'
    headers = {'access_token': api_key}
    response = requests.post(url, headers=headers)
    try:
        response.raise_for_status()
        if response.text:
            logging.debug(f'Debit next charge response: {response.json()}')
            return response.json(), response.status_code
        else:
            return {}, response.status_code
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err} - {response.text}')
    except requests.exceptions.RequestException as err:
        logging.error(f'Error occurred: {err}')
    except ValueError:
        logging.error('Invalid JSON received')
    return {}, response.status_code

# Função para obter todos os clientes com logging
def get_all_customers(api_key):
    url = f'{base_url}/customers'
    headers = {'access_token': api_key}
    response = requests.get(url, headers=headers)
    
    try:
        response.raise_for_status()
        logging.debug(f'All customers received: {response.json()}')
        return response.json(), response.status_code
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err} - {response.text}')
    except requests.exceptions.RequestException as err:
        logging.error(f'Error occurred: {err}')
    except ValueError:
        logging.error('Invalid JSON received')
    
    return {}, response.status_code

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        token = request.form['token']
        session['api_key'] = token
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/')
def index():
    if 'api_key' not in session:
        return redirect(url_for('login'))
    
    api_key = session['api_key']
    subscriptions, status = get_all_subscriptions(api_key)
    customers, _ = get_all_customers(api_key)
    
    if status != 200:
        flash('Erro ao buscar assinaturas. Verifique a chave da API e tente novamente.', 'danger')
    
    return render_template('index.html', subscriptions=subscriptions.get('data', []), customers=customers.get('data', []))

@app.route('/update_subscription', methods=['POST'])
def update_sub():
    if 'api_key' not in session:
        return redirect(url_for('login'))

    api_key = session['api_key']
    subscription_id = request.form['subscription_id']
    new_value = float(request.form['new_value'])
    new_date = request.form['new_date']  # Captura a nova data

    response, status = update_subscription(subscription_id, new_value, new_date, api_key)
    if status == 200:
        flash('Assinatura atualizada com sucesso!', 'success')
    else:
        flash('Erro ao atualizar assinatura.', 'danger')

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

@app.route('/update_due_date', methods=['POST'])
def update_due_date_route():
    if 'api_key' not in session:
        return redirect(url_for('login'))

    payment_id = request.form['payment_id']
    new_due_date = request.form['new_due_date']
    api_key = session['api_key']

    response, status = update_due_date(payment_id, new_due_date, api_key)
    if status == 200:
        flash('Data de vencimento da fatura atualizada com sucesso!', 'success')
    else:
        flash('Erro ao atualizar data de vencimento da fatura.', 'danger')

    return redirect(url_for('index'))

@app.route('/update_subscription_due_date', methods=['POST'])
def update_subscription_due_date_route():
    if 'api_key' not in session:
        return redirect(url_for('login'))

    subscription_id = request.form['subscription_id']
    new_due_date = request.form['new_due_date']
    api_key = session['api_key']

    response, status = update_subscription_due_date(subscription_id, new_due_date, api_key)
    if status == 200:
        flash('Data de vencimento da assinatura atualizada com sucesso!', 'success')
    else:
        flash('Erro ao atualizar data de vencimento da assinatura.', 'danger')

    return redirect(url_for('index'))

@app.route('/debit_next_charge', methods=['POST'])
def debit_next_charge_route():
    if 'api_key' not in session:
        return redirect(url_for('login'))

    subscription_id = request.form['subscription_id']
    api_key = session['api_key']

    response, status = debit_next_charge(subscription_id, api_key)
    if status == 200:
        flash('Próxima cobrança debitada com sucesso!', 'success')
    else:
        flash('Erro ao debitar próxima cobrança.', 'danger')

    return redirect(url_for('index'))

@app.route('/customer/<customer_id>')
def customer(customer_id):
    if 'api_key' not in session:
        return redirect(url_for('login'))

    api_key = session['api_key']
    customer_details, cust_status = get_customer_details(customer_id, api_key)
    customer_payments, pay_status = get_customer_payments(customer_id, api_key)

    if cust_status != 200 or pay_status != 200:
        flash('Erro ao buscar dados do cliente. Verifique a chave da API e tente novamente.', 'danger')

    return render_template('customer.html', customer=customer_details, payments=customer_payments.get('data', []))

if __name__ == '__main__':
    app.run(debug=True)
