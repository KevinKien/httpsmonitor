package main

import (
	"bufio"
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/joho/godotenv"
)

var (
	telegramBotToken string
	telegramChatID   string
	subdomainFilePath string
)

func init() {
	// Load environment variables from .env file
	err := godotenv.Load()
	if err != nil {
		log.Fatalf("Error loading .env file: %v", err)
	}

	telegramBotToken = os.Getenv("TELEGRAM_BOT_TOKEN")
	telegramChatID = os.Getenv("TELEGRAM_CHAT_ID")
	subdomainFilePath = os.Getenv("SUBDOMAIN_FILE_PATH")
}

func main() {
	file, err := os.Open(subdomainFilePath)
	if err != nil {
		log.Fatalf("Error opening file: %v", err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		domain := scanner.Text()
		if domain == "" {
			continue
		}
		fmt.Printf("Processing domain: %s\n", domain)
		checkDomain(domain)
	}

	if err := scanner.Err(); err != nil {
		log.Fatalf("Error reading file: %v", err)
	}
}

func checkDomain(domain string) {
	url := "https://" + domain
	resp, err := http.Get(url)
	if err != nil {
		fmt.Printf("No HTTPS or error checking domain %s: %v\n", domain, err)
		sendTelegramNotification(domain, "No HTTPS or error occurred")
		return
	}
	defer resp.Body.Close()

	if resp.TLS == nil {
		fmt.Printf("No TLS/SSL for domain %s\n", domain)
		sendTelegramNotification(domain, "No HTTPS")
		return
	}

	certs := resp.TLS.PeerCertificates
	if len(certs) > 0 {
		for _, cert := range certs {
			if isCertExpiringSoon(cert) {
				sendTelegramNotification(domain, "Certificate expiring soon")
				return
			}
		}
	}
}

func isCertExpiringSoon(cert *x509.Certificate) bool {
	now := time.Now()
	expiryThreshold := now.AddDate(0, 0, 7) // 7 days from now
	return cert.NotAfter.Before(expiryThreshold)
}

func sendTelegramNotification(domain, message string) {
	client := resty.New()
	resp, err := client.R().
		SetBody(fmt.Sprintf("Domain: %s\nIssue: %s", domain, message)).
		Post(fmt.Sprintf("https://api.telegram.org/bot%s/sendMessage?chat_id=%s", telegramBotToken, telegramChatID))

	if err != nil {
		log.Printf("Error sending notification: %v", err)
		return
	}
	if resp.IsError() {
		log.Printf("Failed to send notification: %s", resp.String())
	}
}
