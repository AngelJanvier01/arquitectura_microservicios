package main

import (
	"encoding/json"
	"fmt"
	"html"
	"log"
	"net/http"
	"os"
	"sync"

	"github.com/gorilla/mux"
)

// Transaction representa una transacción individual
type Transaction struct {
	Amount          int    `json:"amount"`
	TransactionType string `json:"transaction_type"`
	Status          string `json:"status"`
	CreationDate    string `json:"creation_date"`
	TransactionID   string `json:"transaction_id"`
	Source          string `json:"source"`
}

// PaymentRecords representa la estructura completa del JSON
type PaymentRecords map[string][]Transaction

var (
	records     PaymentRecords
	recordsLock sync.RWMutex
)

func main() {
	// Cargar los registros iniciales
	if err := loadRecords(); err != nil {
		log.Fatalf("Error al cargar los registros: %v", err)
	}

	router := mux.NewRouter()
	router.HandleFunc("/", Index)
	router.HandleFunc("/records", GetPayments)
	
	log.Println("Servidor iniciado en el puerto 8003...")
	log.Fatal(http.ListenAndServe(":8003", router))
}

func Index(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Microservicio de pagos, ruta: %q", html.EscapeString(r.URL.Path))
}

// loadRecords carga los registros desde el archivo JSON
func loadRecords() error {
	file, err := os.ReadFile("/volume/simulador/payment_records.json")
	if err != nil {
		return fmt.Errorf("error al leer el archivo: %v", err)
	}

	recordsLock.Lock()
	defer recordsLock.Unlock()

	if err := json.Unmarshal(file, &records); err != nil {
		return fmt.Errorf("error al decodificar JSON: %v", err)
	}

	return nil
}

// GetPayments maneja las solicitudes de registros de pagos
func GetPayments(w http.ResponseWriter, r *http.Request) {
	// Recargar los registros en cada solicitud para obtener los más recientes
	if err := loadRecords(); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	recordsLock.RLock()
	defer recordsLock.RUnlock()

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(records); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}