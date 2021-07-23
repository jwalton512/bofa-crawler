from bofa_crawler.bank import User


class TestUser:
    def test_instantiate(self):
        security_responses = {"foo?": "bar"}
        user = User("online_id", "passcode", security_responses)

        assert user.online_id == "online_id"
        assert user.passcode == "passcode"
        assert user.security_responses == security_responses
