from flask import Flask, request, jsonify
from customer import Customer
from bank import Bank
from db_operation import check_username_exists, check_account_number_exists, get_password
from utils import generate_unique_account_number

app = Flask(__name__)

@app.route('/signup', methods=['POST'])
def handle_signup():
    """
    새로운 사용자 계정을 생성합니다.
    
    요청 본문에는 username, password, name, age, city가 포함되어야 합니다.
    성공 시 새로 생성된 계좌 번호를 반환합니다.
    """
    user_info = request.json
    new_username = user_info.get('username')
    new_password = user_info.get('password')
    full_name = user_info.get('name')
    user_age = user_info.get('age')
    user_city = user_info.get('city')

    # 사용자 이름 중복 체크
    if check_username_exists(new_username):
        return jsonify({"message": "Username Already Exists"}), 400

    # 고유한 계좌 번호 생성
    new_account_number = generate_unique_account_number()
    while check_account_number_exists(new_account_number):
        new_account_number = generate_unique_account_number()

    # 새 고객 생성 및 데이터베이스에 추가
    new_customer = Customer(new_username, new_password, full_name, user_age, user_city, new_account_number)
    new_customer.createuser()
    
    # 새 은행 계좌 생성 및 거래 테이블 생성
    new_bank_account = Bank(new_username, new_account_number)
    new_bank_account.create_transaction_table()

    return jsonify({"message": "SignUp successful", "account_number": new_account_number}), 201

@app.route('/signin', methods=['POST'])
def handle_signin():
    """
    사용자 로그인을 처리합니다.
    
    요청 본문에는 username과 password가 포함되어야 합니다.
    성공 시 로그인 성공 메시지와 사용자 이름을 반환합니다.
    """
    login_info = request.json
    input_username = login_info.get('username')
    input_password = login_info.get('password')

    if check_username_exists(input_username):
        correct_password = get_password(input_username)
        if correct_password == input_password:
            return jsonify({"message": "Sign In Successful", "username": input_username}), 200
        else:
            return jsonify({"message": "Incorrect Password"}), 401
    else:
        return jsonify({"message": "Username Not Found"}), 401

@app.route('/balance', methods=['GET'])
def handle_balance_enquiry():
    """
    계좌 잔액을 조회합니다.
    
    쿼리 파라미터로 username과 account_number가 필요합니다.
    """
    username = request.args.get('username')
    account_number = request.args.get('account_number')
    bank_account = Bank(username, account_number)
    balance = bank_account.balanceequiry()
    return jsonify({"balance": balance}), 200

@app.route('/deposit', methods=['POST'])
def handle_cash_deposit():
    """
    계좌에 입금을 처리합니다.
    
    요청 본문에는 username, account_number, amount가 포함되어야 합니다.
    """
    deposit_info = request.json
    username = deposit_info.get('username')
    account_number = deposit_info.get('account_number')
    amount = deposit_info.get('amount')
    bank_account = Bank(username, account_number)
    bank_account.deposit(amount)
    return jsonify({"message": "Deposit successful"}), 200

@app.route('/withdraw', methods=['POST'])
def handle_cash_withdraw():
    """
    계좌에서 출금을 처리합니다.
    
    요청 본문에는 username, account_number, amount가 포함되어야 합니다.
    잔액 부족 시 오류 메시지를 반환합니다.
    """
    withdraw_info = request.json
    username = withdraw_info.get('username')
    account_number = withdraw_info.get('account_number')
    amount = withdraw_info.get('amount')
    bank_account = Bank(username, account_number)
    result = bank_account.withdraw(amount)
    if result:
        return jsonify({"message": "Withdrawal successful"}), 200
    else:
        return jsonify({"message": "Insufficient balance"}), 400

@app.route('/transfer', methods=['POST'])
def handle_fund_transfer():
    """
    계좌 간 송금을 처리합니다.
    
    요청 본문에는 username, account_number, receiver_account, amount가 포함되어야 합니다.
    송금 실패 시 오류 메시지를 반환합니다.
    """
    transfer_info = request.json
    username = transfer_info.get('username')
    account_number = transfer_info.get('account_number')
    receiver_account = transfer_info.get('receiver_account')
    amount = transfer_info.get('amount')
    bank_account = Bank(username, account_number)
    result = bank_account.fundtransfer(receiver_account, amount)
    if result:
        return jsonify({"message": "Fund transfer successful"}), 200
    else:
        return jsonify({"message": "Fund transfer failed"}), 400

if __name__ == '__main__':
    app.run(debug=True)