class CardSourceRouter:
    """
    card_source 앱(혹은 models)을 card_source DB로 라우팅 (읽기 전용)
    """
    route_app_labels = {"card_source"}  # 우리가 만들 앱 라벨

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "card_source"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return None  # 쓰기 금지
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # default ↔ card_source 관계는 Django FK로 직접 못 엮는 게 안전
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # card_source 쪽은 migrate 금지
        if app_label in self.route_app_labels:
            return False
        return None
