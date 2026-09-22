import dietSupplementImg from "../../assets/다이어트 보조제.png";

// EP03 "슬림스토어" DM 연출용 - 실제로 판매될 법한 다이어트 보조제 사진
export default function DietPillPhoto() {
  return (
    <img
      className="ig-product-photo"
      src={dietSupplementImg}
      alt="슬림스토어가 보낸 다이어트 보조제 사진"
    />
  );
}
