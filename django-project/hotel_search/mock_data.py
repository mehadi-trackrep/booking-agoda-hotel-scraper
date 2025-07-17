class MockDataGenerator:
    @staticmethod
    def get_hotel_search_results():
        # MOCK hotel data
        hotels = [
            {
                "name": "Hotel Grand Palace",
                "image": "https://via.placeholder.com/300x200?text=Hotel+1",
                "rating": "4.5",
                "booking_price": "$150",
                "agoda_price": "$140",
                "best_price": "$140",
                "best_source": "Agoda",
                "url": "https://agoda.com/hotel-grand-palace"
            },
            {
                "name": "City Center Inn",
                "image": "https://via.placeholder.com/300x200?text=Hotel+2",
                "rating": "4.0",
                "booking_price": "$120",
                "agoda_price": "$130",
                "best_price": "$120",
                "best_source": "Booking.com",
                "url": "https://booking.com/city-center-inn"
            }
        ]
        return hotels