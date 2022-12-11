
const rectangleOverlap2 = (rect1, rect2) => {
    const A = { x1: rect1[0], x2:rect1[2]+rect1[0], y1:rect1[1], y2:rect1[1]-rect1[3]};
    const B = { x1: rect2[0], x2:rect2[2]+rect2[0], y1:rect2[1], y2:rect2[1]-rect2[3]};
    console.log(A)
    console.log(B)
    const ca = B.x1 <= A.x2 
    const cb = B.y1 >= A.y2
    const cc = B.x2 >= A.x1
    const cd = B.y2 <= A.y1
    const ca2 = B.x2 <= A.x2
    const cb2 = B.y2 <= A.y2
    if(ca && cb && cc && cd && ca2 && cb2)
    {
        return 1
    }
    if(!ca || !cb || !cc || !cc)
    {
        return 0
    }

    const SA = (A.x2-A.x1)*(A.y1-A.y2)
    const SB = (B.x2-B.x1)*(B.y1-B.y2)
    const SI = Math.max(0, Math.abs(Math.min(A.x2, B.x2) - Math.max(A.x1, B.x1))) * Math.max(0, Math.abs(Math.max(A.y2, B.y2) - Math.min(A.y1, B.y1)))
    const SU = SA + SB - SI
    const overlap_percent = parseFloat(SI)/parseFloat(SU)
    return overlap_percent
  }
//["195","66","265","265"],["195","75","244","244"]
//["193","67","315","315"],["187","72","301","301"]
//["255","44","302","302"],["1","198","143","143"]
  console.log(rectangleOverlap2([195,66,265,265],[195,75,244,244])) 