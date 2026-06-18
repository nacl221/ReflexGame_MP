using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;
using Newtonsoft.Json;

[System.Serializable]
public class GameStateData
{
    public string type;
    public string state;
    public float reaction_time;
    public double timestamp;
}

public class UDPReceiver : MonoBehaviour
{
    [Header("UDP Settings")]
    public int port = 5006;

    [Header("Debug")]
    public bool showDebugLog = true;

    private UdpClient udpClient;
    private Thread receiveThread;
    private bool isReceiving = false;

    public GameStateData latestData;
    public System.Action<GameStateData> OnDataReceived;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        StartReceiving();
    }

    // Update is called once per frame
    void StartReceiving()
    {
        try
        {
            udpClient = new UdpClient(port);
            isReceiving = true;
            
            receiveThread = new Thread(ReceiveData);
            receiveThread.IsBackground = true;
            receiveThread.Start();
            
            Debug.Log($"UDP受信開始: ポート {port}");
        }
        catch (Exception e)
        {
            Debug.LogError($"UDP受信開始エラー: {e.Message}");
        }
    }
    void ReceiveData()
    {
        IPEndPoint remoteEndPoint = new IPEndPoint(IPAddress.Any, 0);

        while (isReceiving)
        {
            try
            {
                byte[] data = udpClient.Receive(ref remoteEndPoint);
                string jsonString = Encoding.UTF8.GetString(data);

                lock (this)
                {
                    latestData = JsonConvert.DeserializeObject<GameStateData>(jsonString);
                }
            }
            catch (Exception e)
            {
                if (isReceiving)
                    Debug.LogError($"UDP受信エラー: {e.Message}");
            }
        }
    }
    void Update()
    {
        if (latestData != null)
        {
            OnDataReceived?.Invoke(latestData);
            latestData = null;
        }
    }
    void OnDestroy()
    {
        StopReceiving();
    }

    void StopReceiving()
    {
        isReceiving = false;
        receiveThread?.Abort();
        udpClient?.Close();
    }
} //参考にしたサイト https://zenn.dev/iuti/articles/0d616d24ebc54c
