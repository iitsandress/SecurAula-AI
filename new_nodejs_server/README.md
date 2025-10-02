# SecurAula-AI - Node.js Dashboard and Agent Setup

This guide provides instructions to set up and run a Node.js server to host the EduMon dashboard, expose it via ngrok, and configure the EduMon agent to connect to it.

## 1. Node.js Server Setup

1.  **Navigate to the server directory:**
    ```bash
    cd new_nodejs_server
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Start the Node.js server:**
    ```bash
    node server.js
    ```
    This will start the server on `http://localhost:3000`. Keep this terminal window open.

## 2. Ngrok Setup

Ngrok is used to create a public URL for your local Node.js server, allowing the agent to connect to it from outside your local network.

1.  **Install Ngrok (if you haven't already):**
    Follow the instructions on the official ngrok website: [https://ngrok.com/download](https://ngrok.com/download)

2.  **Authenticate Ngrok (if you haven't already):**
    You'll need an ngrok account and an authtoken. Get your authtoken from your ngrok dashboard and run:
    ```bash
    ngrok authtoken <YOUR_AUTHTOKEN>
    ```

3.  **Start the Ngrok tunnel:**
    Open a *new* terminal window and run:
    ```bash
    ngrok http 3000
    ```
    Ngrok will provide a public URL (e.g., `https://xxxx-xxxx-xxxx-xxxx.ngrok-free.app`). **Copy this URL**, as you will need it for the agent configuration.

## 3. EduMon Agent Configuration

Now, you need to configure the EduMon agent to connect to your ngrok-exposed server.

1.  **Navigate to the agent directory:**
    ```bash
    cd backup/edumon/agent
    ```

2.  **Create or modify `config.json`:**
    Create a file named `config.json` in this directory (if it doesn't exist) or modify the existing one. Add the following content, replacing `<YOUR_NGROK_URL>` with the URL you copied from the ngrok terminal:

    ```json
    {
      "server_url": "<YOUR_NGROK_URL>",
      "api_key": "S1R4X" 
    }
    ```
    *Note: The `api_key` is set to "S1R4X" as found in `dashboard.py`. Ensure this matches your server's API key if you change it.*

## 4. Run the EduMon Agent

With the server running and the agent configured, you can now start the agent.

1.  **From the `backup/edumon/agent` directory, run the agent:**
    ```bash
    python main.py
    ```
    or if you are using the simple version:
    ```bash
    python main_simple.py
    ```

    The agent should now connect to your Node.js server via the ngrok tunnel.

## Accessing the Dashboard

Open your web browser and go to the ngrok URL you obtained (e.g., `https://xxxx-xxxx-xxxx-xxxx.ngrok-free.app`). You should see the EduMon dashboard. Remember that the dashboard currently displays static content as the dynamic data generation logic from the original Python server is not implemented in the Node.js server.
