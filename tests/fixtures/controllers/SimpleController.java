package welcome.to.the.jungle;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Simple REST controller without base path in RequestMapping.
 */
@RestController
class SimpleController {

    /**
     * Health check endpoint at root level.
     */
    @GetMapping("/health")
    ResponseEntity<String> healthCheck() {
        return ResponseEntity.ok("OK");
    }
}
