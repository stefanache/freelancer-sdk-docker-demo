"""
Freelancer SDK Demo Web Application
Dockerized version based on freelancer-sdk-python examples
"""

from flask import Flask, redirect, request, jsonify, render_template, session
from functools import wraps
import requests
import json
import os

from freelancersdk.session import Session
from freelancersdk.resources.projects.types import MilestoneReason
from freelancersdk.resources.projects import (
    create_local_project, create_country_object, create_location_object,
    create_job_object, create_budget_object, award_project_bid,
    create_milestone_payment, release_milestone_payment, create_currency_object,
    get_bids, create_get_projects_object, get_projects
)
from freelancersdk.exceptions import (
    ProjectNotCreatedException, BidsNotFoundException,
    BidNotAwardedException, MilestoneNotCreatedException,
    MilestoneNotReleasedException, ProjectsNotFoundException,
)

from models import db, User, Project

# Initialize Flask app
app = Flask(__name__)

# Configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:postgres@db:5432/freelancer_demo'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Freelancer API configuration
BASE_URL = os.environ.get('FREELANCER_BASE_URL', 'https://www.freelancer.com')
BASE_ACCOUNTS_URL = os.environ.get('FREELANCER_ACCOUNTS_URL', 'https://accounts.freelancer.com')
CLIENT_ID = os.environ.get('FREELANCER_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('FREELANCER_CLIENT_SECRET', '')
REDIRECT_URI = os.environ.get('REDIRECT_URI', 'http://127.0.0.1:5000/auth_redirect')

# Initialize database
db.init_app(app)

# Global header for OAuth token
h = {"Freelancer-OAuth-V1": ''}


def authenticated(f):
    """
    Decorator that ensures a user is authenticated.
    Use @authenticated on any endpoints you want to protect by OAuth.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        global h
        # if token not set
        if not h["Freelancer-OAuth-V1"]:
            # set it to session token (if it exists)
            if 'Authorization' in session and 'name' in session:
                u = User.query.filter_by(
                    access_token=session["Authorization"],
                    name=session["name"]
                ).first()
                if not u:
                    return auth()
                else:
                    h["Freelancer-OAuth-V1"] = u.access_token
            else:
                return logout()
        return f(*args, **kwargs)
    return decorated


@app.route('/auth')
def auth():
    """Initiate OAuth authorization flow."""
    oauth_uri = BASE_ACCOUNTS_URL + '/oauth/authorise'
    prompt = 'select_account consent'
    advanced_scopes = '1 2 3 4 5 6'
    return redirect(
        '{0}?response_type=code&client_id={1}&redirect_uri={2}&scope=basic&prompt={3}&advanced_scopes={4}'.format(
            oauth_uri, CLIENT_ID, REDIRECT_URI, prompt, advanced_scopes
        )
    )


@app.route('/auth_redirect')
def handle_redirect():
    """Handle OAuth callback and exchange code for access token."""
    global h
    payload = {
        'grant_type': 'authorization_code',
        'code': request.args['code'],
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
    }
    response = requests.post(BASE_ACCOUNTS_URL + '/oauth/token', data=payload).json()

    if 'access_token' not in response:
        return jsonify({'error': 'Failed to get access token', 'details': response}), 400

    h = {"Freelancer-OAuth-V1": response["access_token"]}
    url = BASE_URL + "/api/users/0.1/self/"
    details = requests.get(url, headers=h).json()

    session['Authorization'] = response['access_token']
    session['name'] = details['result']['username']

    user = User.query.filter_by(name=session["name"]).first()
    if not user:
        user = User(
            details['result']['username'],
            details["result"]['email'],
            response['access_token'],
            response['refresh_token']
        )
        db.session.add(user)
    else:
        user.access_token = response['access_token']
        user.refresh_token = response['refresh_token']
    db.session.commit()

    return render_template("user.html", user=user)


@app.route('/logout')
def logout():
    """Clear session and logout user."""
    global h
    session.pop('Authorization', None)
    session.pop('name', None)
    h = {"Freelancer-OAuth-V1": ''}
    return render_template("home.html")


@app.route('/')
def index():
    """Home page."""
    if 'Authorization' in session:
        return render_template("button.html")
    return render_template("home.html")


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Freelancer SDK Demo',
        'database': 'connected' if db.engine else 'disconnected'
    })


@app.route('/create_project', methods=["GET", "POST"])
@authenticated
def post_project():
    """Create a new project on Freelancer."""
    if request.method == "GET":
        return render_template("create_project.html")

    data = {
        'title': "Need someone to buy and bring me a beer ASAP.",
        'description': json.loads(request.data)['description'],
        'budget': create_budget_object(minimum=10, maximum=25),
        'currency': create_currency_object(id=3),
        'jobs': [create_job_object(id=632)],
        'location': create_location_object(
            country=create_country_object('Australia'),
            city='Sydney',
            latitude=-33.8744101,
            longitude=151.2028132,
            full_address="Sydney, NSW, Australia",
        )
    }

    try:
        s = Session(oauth_token=h["Freelancer-OAuth-V1"], url=BASE_URL)
        result = create_local_project(s, **data)
    except ProjectNotCreatedException as e:
        print(f'Error message: {e.message}')
        print(f'Error code: {e.error_code}')
        return jsonify({'error': str(e.message)}), 400
    else:
        user_id = User.query.filter_by(name=session['name']).first().id
        project = Project(result.id, user_id)
        db.session.add(project)
        db.session.commit()
        return jsonify({'result': {'id': result.id, 'seo_url': result.seo_url}})


@app.route('/project/<int:project_id>/bids')
@authenticated
def getbids(project_id):
    """Get bids for a project."""
    get_bids_data = {'project_ids': [project_id]}

    try:
        s = Session(oauth_token=h["Freelancer-OAuth-V1"], url=BASE_URL)
        data = get_bids(s, **get_bids_data)
    except BidsNotFoundException as e:
        print(f'Error message: {e.message}')
        print(f'Server response: {e.error_code}')
        return jsonify({'error': str(e.message)}), 404
    else:
        return jsonify({'result': data})


@app.route('/award/<int:bid_id>', methods=['PUT'])
@authenticated
def award_bid(bid_id):
    """Award a bid to a freelancer."""
    bid_data = {'bid_id': bid_id}

    try:
        s = Session(oauth_token=h["Freelancer-OAuth-V1"], url=BASE_URL)
        data = award_project_bid(s, **bid_data)
    except BidNotAwardedException as e:
        print(f'Error message: {e.message}')
        print(f'Server response: {e.error_code}')
        return jsonify({'error': str(e.message)}), 400
    else:
        return jsonify(data)


@app.route('/create_milestone', methods=["POST"])
@authenticated
def create_milestone():
    """Create a milestone payment."""
    bid_id = json.loads(request.data)['bid_id']
    get_bid_data = {'bid_ids': [bid_id]}

    try:
        s = Session(oauth_token=h["Freelancer-OAuth-V1"], url=BASE_URL)
        response = get_bids(s, **get_bid_data)
    except BidsNotFoundException as e:
        print(f'Error message: {e.message}')
        print(f'Server response: {e.error_code}')
        return jsonify({'error': str(e.message)}), 404

    if len(response['bids']) > 0:
        bid = response['bids'][0]
    else:
        return jsonify({'status': 'error', 'message': 'No bid found.'}), 404

    milestone_data = {
        'project_id': bid['project_id'],
        'bidder_id': bid['bidder_id'],
        'amount': bid['amount'],
        'reason': MilestoneReason.PARTIAL_PAYMENT,
        'description': 'Initial milestone payment',
    }

    try:
        result = create_milestone_payment(s, **milestone_data)
    except MilestoneNotCreatedException as e:
        print(f'Error message: {e.message}')
        print(f'Server response: {e.error_code}')
        return jsonify({'error': str(e.message)}), 400
    else:
        return jsonify({'result': result})


@app.route('/pay/<int:transaction_id>', methods=['POST'])
@authenticated
def pay_milestone(transaction_id):
    """Release a milestone payment."""
    pay_data = {'transaction_id': transaction_id}

    try:
        s = Session(oauth_token=h["Freelancer-OAuth-V1"], url=BASE_URL)
        result = release_milestone_payment(s, **pay_data)
    except MilestoneNotReleasedException as e:
        print(f'Error message: {e.message}')
        print(f'Server response: {e.error_code}')
        return jsonify({'error': str(e.message)}), 400
    else:
        return jsonify({'result': result})


@app.route('/projects')
@authenticated
def list_projects():
    """List user's projects."""
    try:
        s = Session(oauth_token=h["Freelancer-OAuth-V1"], url=BASE_URL)
        project_data = create_get_projects_object(owners=[session.get('user_id')])
        result = get_projects(s, project_data)
    except ProjectsNotFoundException as e:
        print(f'Error message: {e.message}')
        return jsonify({'error': str(e.message)}), 404
    else:
        return jsonify({'result': result})


# Create database tables
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
