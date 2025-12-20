from django.db import models


class FinancialCompany(models.Model):
    """금융회사 정보"""
    dcls_month = models.CharField(max_length=6, blank=True, default='')  # 공시 제출월 (YYYYMM)
    fin_co_no = models.CharField(max_length=20, unique=True)  # 금융회사 코드
    kor_co_nm = models.CharField(max_length=200)  # 금융회사명
    dcls_chrg_man = models.TextField(blank=True, default='')  # 공시 담당자
    homp_url = models.TextField(blank=True, default='')  # 홈페이지 주소
    cal_tel = models.CharField(max_length=100, blank=True, default='')  # 콜센터 전화번호

    def __str__(self):
        return self.kor_co_nm


class DepositProducts(models.Model):
    dcls_month = models.CharField(max_length=6, blank=True, default='')  # 공시 제출월 (YYYYMM)
    fin_prdt_cd = models.CharField(max_length=100, unique=True)  # 금융상품코드 (중복 방지 핵심)
    kor_co_nm = models.TextField()               # 금융회사명
    fin_prdt_nm = models.TextField()             # 금융상품명
    etc_note = models.TextField()                # 금융상품설명
    join_deny = models.IntegerField()            # 가입제한 (1:제한없음, 2:서민전용, 3:일부제한)
    join_member = models.TextField()             # 가입대상
    join_way = models.TextField()                # 가입방법
    spcl_cnd = models.TextField()                # 우대조건

    def __str__(self):
        return self.fin_prdt_nm


class DepositOptions(models.Model):
    product = models.ForeignKey(DepositProducts, on_delete=models.CASCADE, related_name='options')
    fin_prdt_cd = models.CharField(max_length=100)           # 금융상품코드 (연결용)
    intr_rate_type_nm = models.CharField(max_length=100) # 금리 유형명
    intr_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)      # 저축 금리 (금융 계산 필수)
    intr_rate2 = models.DecimalField(max_digits=5, decimal_places=2, null=True)     # 최고 우대 금리
    save_trm = models.IntegerField()             # 저축 기간 (단위: 개월)

    def __str__(self):
        return f"{self.product.fin_prdt_nm} - {self.save_trm}개월"
    
class SavingProducts(models.Model):
    dcls_month = models.CharField(max_length=6, blank=True, default='')  # 공시 제출월 (YYYYMM)
    fin_prdt_cd = models.CharField(max_length=100, unique=True)  # 금융상품코드
    kor_co_nm = models.TextField()               # 금융회사명
    fin_prdt_nm = models.TextField()             # 금융상품명
    etc_note = models.TextField()                # 금융상품설명
    join_deny = models.IntegerField()            # 가입제한
    join_member = models.TextField()             # 가입대상
    join_way = models.TextField()                # 가입방법
    spcl_cnd = models.TextField()                # 우대조건
    max_limit = models.BigIntegerField(null=True, blank=True) # 최고한도 (JSON에 null이 많으므로 허용)

    def __str__(self):
        return self.fin_prdt_nm


class SavingOptions(models.Model):
    product = models.ForeignKey(SavingProducts, on_delete=models.CASCADE, related_name='saving_options')
    fin_prdt_cd = models.CharField(max_length=100)             # 금융상품코드
    intr_rate_type_nm = models.CharField(max_length=100) # 금리 유형명 (단리/복리)
    rsrv_type_nm = models.CharField(max_length=100)      # 적립 유형명 (정액적립식/자유적립식) - 적금에만 있는 필드
    intr_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)      # 저축 금리
    intr_rate2 = models.DecimalField(max_digits=5, decimal_places=2, null=True)     # 최고 우대 금리
    save_trm = models.IntegerField()             # 저축 기간 (개월)

    def __str__(self):
        return f"{self.product.fin_prdt_nm} - {self.save_trm}개월"