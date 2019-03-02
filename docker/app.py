# app.py - a minimal flask api using flask_restful
from flask import Flask
from flask_restful import Resource, Api
from flask_restful_swagger import swagger
from smart_stop import decision_function_bayes

app = Flask(__name__)

###################################
# Wrap the Api with swagger.docs. It is a thin wrapper around the Api class that adds some swagger smarts
api = swagger.docs(Api(app), apiVersion='0.1')
###################################

class DecisionModule(Resource):
    @swagger.operation(
        notes='Decide to continue or not collecting votes over each item',
        nickname='hello',
        parameters=[
            {
                "name": "items",
                "description": "blueprint object that needs to be added. YAML.",
                "required": True,
                "allowMultiple": False,
                "dataType": dict,
            },
            {
                "name": "votes",
                "description": "blueprint object that needs to be added. YAML.",
                "required": True,
                "allowMultiple": False,
                "dataType": dict,
            },
            {
                "name": "ct",
                "description": "Classification Threshold.",
                "required": True,
                "allowMultiple": False,
                "dataType": float,
            },
            {
                "name": "cr",
                "description": "Cost Ratio.",
                "required": True,
                "allowMultiple": False,
                "dataType": float,
            },
            {
                "name": "cf",
                "description": "Classification Function.",
                "required": True,
                "allowMultiple": False,
                "dataType": str,
            }
        ],
    )
    def get(self, items, votes, ct, cr, cf):
        #decision_function_bayes(items, votes, ct, cr, cf)
        return {'hello': 'world'}

api.add_resource(DecisionModule, '/get_decision')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')