import requests
import re

session = requests.Session()

# Step 1: Start OAuth2 flow
start_url = "http://localhost:8080/oauth2/start"
response = session.get(start_url, allow_redirects=True, verify=False)

# Step 2: Get Dex login page URL
dex_login_url = response.url  
print("Dex Login URL:", dex_login_url)  

# Step 3: Extract CSRF, back, and state tokens
csrf_token = None
state_token = None
back_token = None

# Search for hidden fields in the HTML response
csrf_match = re.search(r'name="csrf" value="([^"]+)"', response.text)
state_match = re.search(r'state=([^"&]+)', dex_login_url)
back_match = re.search(r'name="back" value="([^"]+)"', response.text)

if csrf_match:
    csrf_token = csrf_match.group(1)
if state_match:
    state_token = state_match.group(1)
if back_match:
    back_token = back_match.group(1)

print(f"Extracted Tokens - CSRF: {csrf_token}, State: {state_token}, Back: {back_token}")

# Step 4: Send POST request to login
login_data = {
    "login": "user@example.com",
    "password": "12341234",
}
if csrf_token:
    login_data["csrf"] = csrf_token
if back_token:
    login_data["back"] = back_token  # Needed in some Dex versions

auth_response = session.post(dex_login_url, data=login_data, allow_redirects=True, verify=False)

print("After login redirect:", auth_response.url)
print("Session Cookies:", session.cookies.get_dict())  # Check if authservice_session is set

# Step 5: Check authentication by accessing a protected resource
protected_url = "http://localhost:8080/?ns=kubeflow-user-example-com"
protected_response = session.get(protected_url, verify=False)
print(protected_response.request.headers)


if protected_response.status_code == 200:
    print("✅ Successfully authenticated!")
else:
    print("❌ Authentication failed:", protected_response.status_code)


###################
KUBEFLOW_ENDPOINT = "http://localhost:8080/oauth2/start"#"http://localhost:8080"  # Cluster IP and port
KUBEFLOW_USERNAME = "user@example.com"
KUBEFLOW_PASSWORD = "12341234"
MODEL_NAME = "sklearn-iris"#"flower-sample"#"sklearn-iris"
SERVICE_HOSTNAME = "sklearn-iris.kubeflow-user-example-com.example.com"#"flower-sample.some-test.example.com"#"flower-sample.kubeflow-user-example-com.example.com"#"sklearn-iris.kubeflow-user-example-com.example.com"
PREDICT_ENDPOINT = f"http://localhost:8080/v1/models/{MODEL_NAME}:predict" # aq iyo sxvanairad !!!!!!
iris_input = {"instances": [[6.8, 2.8, 4.8, 1.4], [6.0, 3.4, 4.5, 1.6]]}

protected_response = session.post(headers={"Host": SERVICE_HOSTNAME, "Content-Type": "application/json"}, 
                                 url=PREDICT_ENDPOINT,
                                 json=iris_input,
                                 timeout=200,
                                 verify=False)

print(protected_response.status_code)
# print(protected_response.content)

