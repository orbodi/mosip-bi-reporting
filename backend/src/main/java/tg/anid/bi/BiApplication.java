package tg.anid.bi;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

@SpringBootApplication
@ConfigurationPropertiesScan
public class BiApplication {

    public static void main(String[] args) {
        SpringApplication.run(BiApplication.class, args);
    }
}
