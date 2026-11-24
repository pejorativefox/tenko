import java.awt.Font;
import java.awt.Graphics2D;
import java.awt.GraphicsEnvironment;
import java.awt.image.BufferedImage;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Duration;
import java.util.HexFormat;
import java.util.concurrent.atomic.AtomicBoolean;
import javax.net.ssl.TrustManagerFactory;
import javax.net.ssl.X509TrustManager;

/** Offline package checks; an optional URL also exercises HTTPS after install. */
public class JavaSmoke {
    public static void main(String[] args) throws Exception {
        if (Runtime.version().feature() != 21) {
            throw new AssertionError("Java 21 is required");
        }

        AtomicBoolean virtual = new AtomicBoolean();
        Thread thread = Thread.startVirtualThread(
            () -> virtual.set(Thread.currentThread().isVirtual()));
        thread.join();
        if (!virtual.get()) {
            throw new AssertionError("Virtual thread did not run");
        }

        String digest = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256")
            .digest("abc".getBytes(StandardCharsets.UTF_8)));
        if (!digest.equals(
                "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")) {
            throw new AssertionError("SHA-256 failed");
        }

        TrustManagerFactory factory = TrustManagerFactory.getInstance(
            TrustManagerFactory.getDefaultAlgorithm());
        factory.init((java.security.KeyStore) null);
        int anchors = 0;
        for (var manager : factory.getTrustManagers()) {
            if (manager instanceof X509TrustManager x509) {
                anchors += x509.getAcceptedIssuers().length;
            }
        }
        if (anchors == 0) {
            throw new AssertionError("No trusted certificate authorities");
        }

        if (GraphicsEnvironment.getLocalGraphicsEnvironment()
                .getAvailableFontFamilyNames().length == 0) {
            throw new AssertionError("No fonts available");
        }
        BufferedImage image = new BufferedImage(160, 40, BufferedImage.TYPE_INT_ARGB);
        Graphics2D graphics = image.createGraphics();
        try {
            graphics.setFont(new Font(Font.SANS_SERIF, Font.PLAIN, 16));
            graphics.drawString("Tenko Java 21", 4, 24);
        } finally {
            graphics.dispose();
        }

        if (args.length > 0) {
            try (HttpClient client = HttpClient.newBuilder()
                    .connectTimeout(Duration.ofSeconds(20))
                    .followRedirects(HttpClient.Redirect.NORMAL).build()) {
                var request = HttpRequest.newBuilder(URI.create(args[0]))
                    .timeout(Duration.ofSeconds(30)).GET().build();
                var response = client.send(request, HttpResponse.BodyHandlers.discarding());
                if (response.statusCode() != 200) {
                    throw new AssertionError("HTTPS returned " + response.statusCode());
                }
                System.out.println("HTTPS OK: " + args[0]);
            }
        }
        System.out.println("Java 21 smoke checks passed; trusted CAs: " + anchors);
    }
}
