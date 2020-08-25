package boundary;

import java.io.*;
import java.net.Socket;

public class CommunicationManager {
    public static final String HOST = "192.168.4.4";
    public static final int PORT = 8000;

    private static CommunicationManager commMgr = null;

    private Socket conn = null;
    private BufferedWriter writer;
    private BufferedReader reader;

    // Message Types
    // Android -> PC
    public static final String MSG_EX_START = "EX_START";
    public static final String MSG_FP_START = "FP_START";

    // PC -> Android
    public static final String MSG_MAP = "MAP";
    public static final String MSG_BOT_POS = "BOT_POS";

    // PC -> Arduino
    public static final String MSG_BOT_MOVE = "BOT_MOVE";

    // Arduino -> PC
    public static final String MSG_SENSOR = "SENSOR";


    private CommunicationManager() {}

    public static CommunicationManager CommunicationManager() {
        if (commMgr == null)
            commMgr = new CommunicationManager();

        return commMgr;
    }

    public void openConnection() {
        System.out.println("Opening connection...");

        try {
            conn = new Socket(HOST, PORT);

            OutputStream os = conn.getOutputStream();
            writer = new BufferedWriter(new OutputStreamWriter(os));

            InputStream is = conn.getInputStream();
            reader = new BufferedReader(new InputStreamReader(is));

            System.out.println("Connection successfully established.");

        } catch (Exception e) {
            System.out.println(e.toString());
        }
    }

    public void closeConnection() {
        System.out.println("Closing connection...");

        try {
            reader.close();

            if (conn != null) {
                conn.close();
                conn = null;
            }

            System.out.println("Connection closed.");

        } catch (Exception e) {
            System.out.println(e.toString());
        }
    }

    public void sendMessage(String msgType, String msg) {
        System.out.println("Sending a message...");

        try {
            String outputMsg;

            if (msg == null) {
                outputMsg = msgType + "\n";

            } else {
                outputMsg = msgType + ": " + msg + "\n";
            }

            writer.write(outputMsg);
            writer.flush();

            System.out.println("Message sent:" + outputMsg);

        } catch (Exception e) {
            System.out.println(e.toString());
        }
    }

    public String receiveMessage() {
        System.out.println("Receiving a message...");

        try {
            String input = reader.readLine();

            if (input != null && input.length() > 0) {
                System.out.println("Message received: " + input);
                return input;
            }

        } catch (Exception e) {
            System.out.println(e.toString());
        }

        return null;
    }

    public boolean isConnected() {
        return conn.isConnected();
    }
}
