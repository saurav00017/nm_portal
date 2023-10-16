from datarepo.models import StudentCaste, CollegeType


class Config:
    CASTE: int = None
    COLLEGE_TYPE: int = None
    COLLEGE_SUBSCRIPTION_FEE = 12000 * 100  # 10,000 /-
    COLLEGE_SUBSCRIPTION_YEARS = 2
    STUDENT_SUBSCRIPTION_FEE = 1000 * 100  # 1000 /-
    FRONT_END_URL = 'https://sandbox-portal.naanmudhalvan.in'
    STUDENT_SUBSCRIPTION_YEARS = 5

    def __init__(self, caste: int = None, college_type: int = None):

        if college_type:
            self.COLLEGE_TYPE = int(college_type)
            if self.COLLEGE_TYPE != CollegeType.ENGINEERING:
                self.STUDENT_SUBSCRIPTION_FEE = 500 * 100  # 500/-
                # print("ENTERED COLLEGE_TYPE")

        if caste:
            self.CASTE = int(caste)
            if self.CASTE in [StudentCaste.SC, StudentCaste.ST]:
                self.STUDENT_SUBSCRIPTION_FEE = self.STUDENT_SUBSCRIPTION_FEE / 2
                # print("ENTERED CASTE", self.STUDENT_SUBSCRIPTION_FEE)

        # print('CollegeType.ENGINEERING', CollegeType.ENGINEERING)
        # print('StudentCaste.CASTE', [StudentCaste.SC, StudentCaste.ST])
        # print('Config', self.CASTE)
        # print('Config', self.COLLEGE_TYPE)
        # print('Config', self.STUDENT_SUBSCRIPTION_FEE)

    def get_student_fee(self):
        if self.COLLEGE_TYPE != CollegeType.ENGINEERING:
            self.STUDENT_SUBSCRIPTION_FEE = 500 * 100  # 500/-

        print(type(self.CASTE), self.CASTE in [StudentCaste.SC, StudentCaste.ST])
        if self.CASTE in [StudentCaste.SC, StudentCaste.ST]:
            self.STUDENT_SUBSCRIPTION_FEE = self.STUDENT_SUBSCRIPTION_FEE / 2
            print("ENTERED CASTE", self.STUDENT_SUBSCRIPTION_FEE)

        return self.STUDENT_SUBSCRIPTION_FEE

    # allow upload big file
    DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 2  # 2M
    FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 2  # 2M

