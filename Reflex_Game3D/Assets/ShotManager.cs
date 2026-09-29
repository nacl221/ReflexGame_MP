using Unity.VisualScripting;
using UnityEditor.Experimental.GraphView;
using UnityEngine;

public class ShotManager : MonoBehaviour
{
    public UDPReceiver udpReceiver;
    
    [Header("撃たれるオブジェクト")]
    public TargetObject target1;
    public TargetObject target2;
    [Header("設定値")]
    public float pushForce = 1000f;

    private bool hasFiredInThisRound = false;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    
    void Start()
    {
        if(udpReceiver != null)
        {
            udpReceiver.OnDataReceived += HandleGameState;
        }
    }

    // Update is called once per frame
    void HandleGameState(GameStateData data)
    {
        Debug.Log("Pythonから届いたステート: " + data.state);

        if (data.state == "RESULT")
        {

            if (!hasFiredInThisRound)
            {
                if (target1 != null) target1.OnShotRandom(pushForce);
                if (target2 != null) target2.OnShotRandom(pushForce);

                hasFiredInThisRound = true;
                Debug.Log("オブジェクトは撃たれたよ。反応時間:" + data.reaction_time);
            }

        }
        else if (data.state == "READY" || data.state == "WAITING")
        {
            hasFiredInThisRound = false;
        }
    }
    void OnDestroy()
    {
        if(udpReceiver != null)
        {
        udpReceiver.OnDataReceived -= HandleGameState;
        }
    }
}
