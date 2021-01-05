from instamojo_wrapper import Instamojo
API_KEY="test_9164b347a409e48074787f2dc03"
AUTH_TOKEN="test_4b25549bb1b8910bd6ddf80e5e6"
api = Instamojo(api_key=API_KEY, auth_token=AUTH_TOKEN,endpoint='https://test.instamojo.com/api/1.1/');

# Create a new Payment Request
response = api.payment_request_create(
    amount='10',
    purpose='testing',
    send_email=True,
    email="sweetipandit89@gmail.com",
    redirect_url="http://localhost:8000/handle_redirect.py"
    )

# print the long URL of the payment request.
print(response['payment_request']['longurl'])
# print the unique ID(or payment request ID)
print(response['payment_request']['id'])