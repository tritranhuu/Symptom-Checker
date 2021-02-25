
QUESTION_GET_SYMPTOM = {
    "vi" : {
        "confirm_question": "Bạn có thể xác nhận lại những triệu chứng bạn gặp phải ?",
        "pick_question": "Theo bạn, đâu là triệu chứng chính và ảnh hưởng nặng nhất ?"
    },
    "en" : {
        "confirm_question": "Could you confirm the symptoms that you had ?",
        "pick_question": "Which is the most annoying symptom to you ?"
    }
}


QUESTION_SYMPTOM_INIT_INFO = {
    "vi" : {
        "where" : {
            "question" : "Bạn %s ở đâu ?"
        },
        "when" : {
            "question" : "Bạn %s khi nào ?"
        },
        "how" : {
            "question" : "Bạn %s như thế nào ?"
        }
    },

    "en" : {
        "where" : {
            "question" : "Where do you have %s ?"
        },
        "when" : {
            "question" : "When do you have %s ?"
        },
        "how" : {
            "question" : "How do you feel about your %s ?"
        }
    }
}

QUESTION_SEVERITY = {
    "vi" : [
        {
            "question" : "Hầu hết các triệu chứng trên xuất hiện bao lâu rồi ?",
            "answer" : ["Cách đây vài giờ", "Cách đây vài ngày", "Đã xuất hiện từ vài tháng", "Đã xuất hiện nhiều năm"]
        },
        {
            "question" : "Nếu đánh giá mức độ nặng tăng dần từ 1 (bị nhẹ) đến 5 (rất nặng), thì triệu chứng bệnh này có giá trị bao nhiêu",
            "answer" : ["1 - Nhẹ nhàng","2 - Khá khó chịu","3 - Rất khó chịu","4 - Đau đớn","5 - Gay gắt không chịu nổi"]
        },
        {
            "question" : "Các triệu chứng có tiến triển như nào ?",
            "answer" : ["Kéo dài và không dứt", "Lúc bị lúc không", "Ngày càng nặng thêm", "Ngày càng giảm nhẹ dần"]
        }
    ],
    "en" : [
        {
            "question" : "How long have you had your symptoms ?",
            "answer" : ["For few hours", "For few days", "For few months", "For few years"]
        },
        {
            "question" : "On a scale of 1(mild) to 5(severe), how do you score your symptoms ?",
            "answer" : ["1 - Mild","2 - Uncomfortable","3 - Distracting","4 - Intense","5 - Severe"]
        },
        {
            "question" : "How have all your symptoms processed ?",
            "answer" : ["Lasting for long time", "Sometimes have somtimes not", "More and more severe", "More and more mild"]
        }
    ]
}

QUESTION_SYMPTOM = {
    "vi" : {
        "multiple" : "Bạn có bị triệu chứng nào trong số các triệu chứng sau không ?",
        "single" : "Bạn có bị %s không?"
    },
    "en" : {
        "multiple" : "Do you also have any of these symptoms ?",
        "single" : "Do you have any problem with %s ?"
    }
}

QUESTION_CAUSE = {
    "vi" : {
        "multiple" : "Bạn có thói quen hay hoạt động nào dưới đây không ?",
        "single" : "Bạn có %s không?",
        "genetic" : "Có ai trong gia đình bạn mặc bệnh %s không ?",
        "infection" : "Bạn có đến những nơi có dịch %s hay tiếp xúc với ai nhiễm không ?"
    },
    "en" : {
        "multiple" : "Do you have any of these recent for daily activities below ?",
        "single" : "Do you %s ?",
        "genetic" : "Is there anyone in your family had been diagnosed with %s ?",
        "infection" : "Have you been to anywhere that have %s or met anyone who infected ?"
    }
}

QUESTION_DISEASE = {
    "vi" : {
        "multiple" : "Bạn có mắc phải những bệnh nào dưới đây không ?",
        "single": "Bạn có mắc bệnh %s không?"
    },
    "en" : {
        "multiple" : "Do you also have any of these diseases ?",
        "single": "Have you been diagnosed with %s ?"
    }
}

ANSWER_SINGLE = {
    "vi" : ["Có", "Không"],
    "en" : ["Yes", "No"]
}

SYMPTOM_PROGRESS = {
                    "Kéo dài và không dứt" : 2, "Lasting for long time" : 2,   
                    "Lúc bị lúc không" : 1, "Sometimes have somtimes not" : 1,
                    "Ngày càng nặng thêm" : 3, "More and more severe" : 3,
                    "Ngày càng giảm nhẹ dần" : -3, "More and more mild" : -3

                    }

SYMPTOM_TIME = {
                "Cách đây vài giờ" : 1, "For few hours" : 1,   
                "Cách đây vài ngày" : 2, "For few days" : 2,
                "Đã xuất hiện từ vài tháng" : 3, "For few months" : 3,
                "Đã xuất hiện nhiều năm" : 4, "For few years" : 4
                }

SYMPTOM_LEVEL = range(1,5)

RECOMMEND = {
        1 : "Với mức độ nguy cơ về sức khỏe bạn đang gặp phải, DAISA khuyên bạn nên chăm lo đến sức khỏe hàng ngày của bạn hơn nữa, thay đổi chế độ ăn uống, nghỉ ngơi, tập luyện thể chất để chủ động phòng bệnh. Tuy mức độ nhiễm bệnh của bạn đang nhẹ, nhưng đã có dấu hiệu sớm về bệnh, DAISA khuyên bạn nên đặt hẹn khám từ xa với bác sĩ để được chăm sóc phòng tránh đúng cách. Hiện tại DAISA đã xây dựng được mang lưới phòng khám, bệnh viện rất uy tín, DAISA sẽ giúp bạn đặt hẹn khám từ xa phù hợp nhất ở bước tiếp theo.",
        2 : "DAISA cho rằng bạn đang gặp vấn đề về sức khỏe và có thể dẫn đến tình trạng bệnh nặng hơn. DAISA khuyên bạn nên đặt hẹn ngay với bác sĩ để được tư vấn khám bệnh tốt nhất. DAISA đang hợp tác với mạng lưới phòng khám, bệnh viện uy tín với các chuyên gia hàng đầu, trong bước tiếp theo DAISA sẽ giúp bạn đặt hẹn đến bệnh viện, phòng khám, bác sĩ phù hợp nhất cho bạn.",
        3 : "Với mức độ nhiệm bệnh hiện tại, DAISA có phần lo lắng cho bạn, DAISA khuyên bạn nên đến ngay cơ sở y tế gần nhất đề được khám bệnh. DAISA đang hợp tác với mạng lưới phòng khám, bệnh viện uy tín với các chuyên gia hàng đầu, trong bước tiếp theo DAISA sẽ giúp bạn đặt hẹn đến bệnh viện, phòng khám, bác sĩ phù hợp nhất cho bạn."
}