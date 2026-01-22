package welcome.to.the.jungle;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import jakarta.validation.Valid;

/**
 * REST controller for payment operations with multiple endpoints.
 */
@RestController
@RequestMapping("/api/payment")
class PaymentController {

    /**
     * Confirms a payment from external provider callback.
     */
    @PostMapping("/confirmation")
    ResponseEntity<Void> confirmPayment(@Valid @RequestBody PaymentRequest request) {
        return ResponseEntity.noContent().build();
    }

    /**
     * Get payment status.
     */
    @GetMapping("/status")
    ResponseEntity<PaymentStatus> getPaymentStatus() {
        return ResponseEntity.ok().build();
    }

    /**
     * Update payment information.
     */
    @PutMapping("/update")
    ResponseEntity<Void> updatePayment(@RequestBody PaymentUpdateRequest request) {
        return ResponseEntity.ok().build();
    }

    /**
     * Delete a payment record.
     */
    @DeleteMapping("/cancel")
    ResponseEntity<Void> cancelPayment() {
        return ResponseEntity.noContent().build();
    }
}
