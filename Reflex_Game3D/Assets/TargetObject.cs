using UnityEngine;

public class  TargetObject: MonoBehaviour
{
    private Rigidbody rb;
    private Collider col;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        rb = GetComponent<Rigidbody>();
        col = GetComponent<Collider>();
    }

    public void OnShotRandom(float force)
    {
        if (rb == null || col == null) return;

        Vector3 randomPoint = new Vector3(
            Random.Range(col.bounds.min.x, col.bounds.max.x),
            Random.Range(col.bounds.min.y, col.bounds.max.y),
            Random.Range(col.bounds.min.z, col.bounds.max.z)
        );
        float randomYaw = Random.Range(-15f, 15f);
        float randomPitch = Random.Range(35f, 55f);

        Quaternion randomRotation = Quaternion.Euler(-randomPitch, randomYaw, 0f);
        Vector3 restrictedRandomDirection = randomRotation * Vector3.forward;

        rb.AddForceAtPosition(restrictedRandomDirection *force, randomPoint, ForceMode.Impulse);
    }
}
