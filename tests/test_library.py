
def test_late_return_fine(self):
    library.borrow(
        self.connection, "M1", 1, self.today
    )

    fine = library.return_book(
        self.connection,
        "M1",
        1,
        self.today + timedelta(days=17)
    )

    self.assertEqual(fine, 3)
