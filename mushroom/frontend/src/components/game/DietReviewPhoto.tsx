import dietReviewImg from "../../assets/다이어트 후기.png";

// EP03 "슬림스토어" DM 연출용 - 판매자가 보내는 "후기 인증샷" 캡처 이미지
export default function DietReviewPhoto() {
  return (
    <img
      className="ig-review-photo"
      src={dietReviewImg}
      alt="슬림스토어가 보낸 다이어트 후기 인증샷"
    />
  );
}
