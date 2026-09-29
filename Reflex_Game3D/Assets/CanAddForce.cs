using UnityEngine;

public class CanAddForce : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    private Rigidbody rb;
    void Start()
    {
        //遠くに飛ばす
        rb = GetComponent<Rigidbody>();
        Vector3 force = new Vector3(0.0f, 3.0f, 3.0f);
        rb.AddForce(force, ForceMode.Impulse);
        rb.AddTorque(Vector3.up * 100f, ForceMode.Impulse);
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    void OnCollisionEnter(Collision collision)
    {
        Debug.Log("衝突した相手: " + collision.gameObject.name); // ログを表示する
        if (collision.gameObject.CompareTag("Plane"))
        {
            rb.linearDamping = 5f;          // 移動の抵抗を増やす（デフォルトは 0）
            rb.angularDamping = 5f;
        }

    }
}
