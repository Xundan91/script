from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)


def calculate_user_rating(data):
    W_ratio = 0.4  
    W_timing = 0.3  
    W_success = 0.3  

    
    df = pd.DataFrame(data)

    
    df['return_request_ratio'] = df['return_requests'] / df['total_orders']

    # Apply user rating formula
    df['user_rating'] = (W_ratio * (1 - df['return_request_ratio'])) + \
                        (W_timing * df['avg_return_timing']) + \
                        (W_success * df['return_success_rate'])

    
    df['user_rating'] = df['user_rating'].clip(lower=0.1, upper=1.0)

    # Segmentation Logic
    def segment_user(row):
        if row['return_request_ratio'] > 0.5:
            return 'Frequent Returner'
        elif row['return_success_rate'] >= 0.8 and row['return_request_ratio'] <= 0.2:
            return 'High Value Customer'
        elif row['avg_return_timing'] < 0.3:
            return 'Late Returner'
        else:
            return 'Neutral'

    df['segment'] = df.apply(segment_user, axis=1)

    # Convert to a dictionary for output
    return df[['user_id', 'user_rating', 'segment']].to_dict(orient='records')

# Define API endpoint
@app.route('/analyze', methods=['POST'])
def analyze_data():
    user_data = request.json
    result = calculate_user_rating(user_data)
    return jsonify(result)

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000)
