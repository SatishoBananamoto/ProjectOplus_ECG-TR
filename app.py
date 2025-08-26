# app.py - The Flask Demo Application (v1.1 - Final Demo Version)
from flask import Flask, request, jsonify, render_template
from tr_engine import System, Entity, Cycle, TaskCreditLedger, Constitution, TR_execute
import logging
import random

# In a real app, you would import the validated tr_engine
# For this guide, ensure tr_engine.py is in the same directory.

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    """Serves the main demo page."""
    return render_template('index.html')

@app.route('/tr/optimize', methods=['POST'])
def optimize_system():
    """API endpoint to run EGC + TR on user-provided system states."""
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ["entities", "cycle_length", "cycle_phases", "target_state"]):
            return jsonify({"error": "Missing required fields"}), 400
        
        entities = [Entity(id=e["id"], state=float(e["state"]), stable_states=set(e["stable_states"])) for e in data["entities"]]
        cycle = Cycle(length=int(data["cycle_length"]), phases=int(data["cycle_phases"]))
        constitution = Constitution(priorities=data.get("priorities", []))
        
        system = System(
            entities=entities,
            cycle=cycle,
            target_state=float(data["target_state"]),
            config={"MAX_TOLERANCE": 1.0, "NOISE_COEFFICIENT": data.get("noise_coefficient", 0.05)},
            constitution=constitution
        )
        
        logging.info(f"Processing system: {data}")
        updated_system, success = TR_execute(system)
        
        if not success:
            return jsonify({"error": "TR execution failed. Check constraints."}), 500
        
        response = {
            "success": True,
            "final_state": {
                "entities": [{"id": e.id, "state": e.state} for e in updated_system.entities],
                "ledger": {
                    "excess_credit": updated_system.ledger.excess,
                    "next_cycle_id": updated_system.ledger.cycle_id
                }
            }
        }
        logging.info(f"Output: {response}")
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 400

# Note: The /tr/simulate and /tr/visualize endpoints will be used for the full Eclipse IoT demo.
# The basic optimize endpoint is sufficient for our first local test.

if __name__ == '__main__':
    app.run(debug=True, port=5001)
