# app.py - The Flask Demo Application (v1.0 Final)
from flask import Flask, request, jsonify
from tr_engine import System, Entity, Cycle, TaskCreditLedger, Constitution, TR_execute
import logging
import random

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

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

# Placeholder for /tr/simulate and /tr/visualize endpoints
@app.route('/tr/simulate', methods=['POST'])
def simulate_iot():
    """This endpoint will contain the full simulation logic."""
    # This is where the logic for the control experiment vs. EGC+TR experiment would go.
    return jsonify({"message": "Simulation endpoint to be fully implemented."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
