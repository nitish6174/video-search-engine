from flask import Blueprint,request,render_template,redirect

routes_module = Blueprint('routes_module', __name__)


@routes_module.route('/', methods=["GET"])
def homePage():
    if request.method == 'GET':
        return render_template('home.html')