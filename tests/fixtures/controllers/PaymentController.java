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
import lombok.extern.log4j.Log4j2;

/**
 * REST controller for payment operations with multiple endpoints.
 */
@Log4j2
@RestController
@RequestMapping("/api/payment")
class PaymentController {

    /**
     * Confirms a payment from external provider callback.
     */
    @PostMapping("/confirmation")
    ResponseEntity<Void> confirmPayment(@Valid @RequestBody PaymentRequest request) {
        LOGGER.info("Confirming payment. Transaction id: '{}'. Provider: '{}'",
                request.paymentIdentifier(), request.paymentProvider());
        return ResponseEntity.noContent().build();
    }

    /**
     * Get payment status.
     */
    @GetMapping("/status")
    ResponseEntity<PaymentStatus> getPaymentStatus() {
        LOGGER.debug("Getting payment status");
        return ResponseEntity.ok().build();
    }

    /**
     * Update payment information.
     */
    @PutMapping("/update")
    ResponseEntity<Void> updatePayment(@RequestBody PaymentUpdateRequest request) {
        LOGGER.info("Updating payment for id: {}", request.getId());
        return ResponseEntity.ok().build();
    }

    /**
     * Delete a payment record.
     */
    @DeleteMapping("/cancel")
    ResponseEntity<Void> cancelPayment() {
        LOGGER.warn("Payment cancellation requested");
        return ResponseEntity.noContent().build();
    }
}
