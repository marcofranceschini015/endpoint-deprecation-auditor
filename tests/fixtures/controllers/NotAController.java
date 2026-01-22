package welcome.to.the.jungle;

import org.springframework.stereotype.Service;

/**
 * This is a Service class, not a REST controller.
 */
@Service
class PaymentService {

    public void processPayment() {
        // Business logic here
    }

    public String getPaymentStatus() {
        return "COMPLETED";
    }
}
