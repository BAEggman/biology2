// A scene supplies the default topic. A lesson ID can override it when tours in
// the same scene teach different chapters. Related links never add to the count.
const units = [
  { title: '세포생물학', topics: [
    { id: 'cell-structure', title: '세포 구조·세포골격·막수송', scenes: ['s14','s48','s52','s53'], related: {
      L03c: '세균·고세균·진핵세포 비교', L08b: '액틴과 마이오신이 만드는 근절'
    }},
    { id: 'cell-signaling', title: '수용체와 세포 신호전달', scenes: ['s16'], related: {
      L23b: '아세틸콜린의 채널형·GPCR 수용체', L23c: '아드레날린 수용체', L17f: 'ADH에 의한 물 통로 조절'
    }},
    { id: 'cell-cycle', title: '세포주기·분열·검문소', scenes: ['s19'], lessons: ['L48a','L48b'], related: {
      L14b: '미세소관과 중심체', L11a: 'S기의 DNA 복제'
    }},
    { id: 'cell-death', title: '아폽토시스와 괴사', lessons: ['L19e','L19f','L19g'], related: {
      L19d: 'DNA 손상과 p53'
    }}
  ]},
  { title: '분자생물학·유전학', topics: [
    { id: 'dna', title: 'DNA 구조·복제·수선', scenes: ['s38','s11'], related: {
      L19c: '복제 면허와 재복제 방지', L19d: '손상 DNA를 감시하는 p53'
    }},
    { id: 'gene-expression', title: '염색질·유전자 발현과 조절', scenes: ['s37','s43','s10','s25'], related: {
      L03a: '수평적 유전자 전달', L48c: 'mRNA와 리보솜 소단위체의 핵 밖 이동'
    }}
  ]},
  { title: '생화학·물질대사', topics: [
    { id: 'cell-respiration', title: '해당과정·발효·세포호흡', scenes: ['s31','s32'], related: {
      L49b: '간의 글리코젠 대사와 당신생', L12c: '탈탄산과 비타민 B1', L12d: '생합성 반응과 비타민 조효소'
    }},
    { id: 'photosynthesis', title: '광합성·탄소고정·광호흡', scenes: ['s45'], related: {
      L20d: '기공 개폐와 광호흡'
    }},
    { id: 'vitamins', title: '비타민·조효소·결핍증', lessons: ['L12c','L12d','L12e'], related: {
      L12b: '소장에서의 흡수와 운반'
    }}
  ]},
  { title: '인체·동물생리학', topics: [
    { id: 'homeostasis', title: '조직·기관계와 항상성', scenes: ['s50'], related: {
      L14a: '세포연접과 상피', L46d: '조직액과 림프의 순환'
    }},
    { id: 'endocrine', title: '내분비·혈당 조절', scenes: ['s07','s49'], related: {
      L17b: '레닌–안지오텐신–알도스테론계', L17f: 'ADH와 집합관', L51a: '생식샘과 성호르몬'
    }},
    { id: 'muscle', title: '근육과 수축', scenes: ['s08'], related: {
      L14b: '액틴 미세섬유', L23b: '신경근접합부의 니코틴성 수용체'
    }},
    { id: 'renal', title: '신장·배설·수분과 전해질', scenes: ['s17'], related: {
      L07d: '부신피질의 알도스테론', L07a: '시상하부와 뇌하수체 후엽의 ADH', L46d: '혈압과 체액 조절'
    }},
    { id: 'nervous', title: '신경·감각·자율신경', scenes: ['s15','s23'], related: {
      L16d: '뉴런·반사·국소 신호', L08a: '근육의 흥분–수축 연결'
    }},
    { id: 'circulation', title: '심장·혈관·혈액', scenes: ['s46'], related: {
      L17b: '콩팥을 통한 혈압 조절', L46g: '적혈구의 산소 운반'
    }},
    { id: 'immune', title: '면역 — 선천 방어와 적응 면역', scenes: ['s13'] },
    { id: 'breathing', title: '호흡과 기체 운반', lessons: ['L46f','L46g'], related: {
      L46a: '폐순환과 체순환', L46h: '아가미 역류교환과 비교순환'
    }},
    { id: 'digestion', title: '소화·흡수와 간', scenes: ['s12'], related: {
      L49b: '간의 대사와 담즙', L12e: '수용성·지용성 비타민 흡수'
    }},
    { id: 'reproduction', title: '생식과 동물 발생', scenes: ['s51'], lessons: ['L04a'], related: {
      L07b: '뇌하수체의 생식샘자극호르몬', L46h: '태아순환'
    }}
  ]},
  { title: '미생물·생물다양성·진화', topics: [
    { id: 'microbes', title: '바이러스·세균·고세균', scenes: ['s01','s03'], related: {
      L25a: '세균의 lac 오페론', L25b: '세균의 trp 오페론', L11b: '대장균 DNA 중합효소'
    }},
    { id: 'fungi', title: '균류의 분류와 생활사', scenes: ['s05'], related: {
      L22d: '뿌리와 균류의 공생'
    }},
    { id: 'animals', title: '동물 계통과 비교', scenes: ['s04'], related: {
      L04a: '배엽·난할·원구의 운명', L46h: '동물군별 순환과 호흡', L17c: '동물군별 질소 노폐물'
    }},
    { id: 'evolution', title: '집단유전학과 진화', scenes: ['s35'], related: {
      L36a: '식물의 육상 진출'
    }}
  ]},
  { title: '식물생물학', topics: [
    { id: 'plant-diversity', title: '식물 계통·생활사·생식', scenes: ['s36','s34'], related: {
      L20c: '광주기와 개화'
    }},
    { id: 'plant-transport', title: '식물 조직·수송·영양', scenes: ['s22'], related: {
      L20d: '기공과 수분 손실', L05a: '균근의 영양 교환'
    }},
    { id: 'plant-regulation', title: '식물 호르몬·광주기·굴성', scenes: ['s20'], related: {
      L45e: '광호흡과 C₄·CAM 식물', L22b: '증산과 물의 상승'
    }}
  ]}
];

function lessonTopics(lessons) {
  const sceneTopics = new Map(), lessonOverrides = new Map(), topicsById = new Map();
  const groups = units.map(unit => ({
    title: unit.title,
    topics: unit.topics.map(topic => {
      const item = { id: topic.id, title: topic.title, main: [], related: [] };
      if (topicsById.has(item.id)) throw new Error('중복 목차 항목: ' + item.id);
      topicsById.set(item.id, item);
      for (const [map, ids] of [[sceneTopics, topic.scenes], [lessonOverrides, topic.lessons]]) {
        for (const id of ids || []) {
          if (map.has(id)) throw new Error('목차 분류가 중복된 묶음 또는 과: ' + id);
          map.set(id, item);
        }
      }
      return item;
    })
  }));
  const byId = new Map(lessons.map(lesson => [lesson.id, lesson]));
  const pending = { id: 'uncategorized', title: '새로 추가된 과', main: [], related: [] };
  for (const lesson of lessons) {
    const owner = lessonOverrides.get(lesson.id) || sceneTopics.get(lesson.scene) || pending;
    owner.main.push(lesson);
  }
  for (const unit of units) for (const topic of unit.topics) {
    const item = topicsById.get(topic.id);
    for (const [id, label] of Object.entries(topic.related || {})) {
      const lesson = byId.get(id);
      if (lesson && !item.main.includes(lesson)) item.related.push({ id, label });
    }
  }
  if (pending.main.length) groups.push({ title: '분류 대기', topics: [pending] });
  return groups.map(g => ({...g, topics:g.topics.filter(t => t.main.length)})).filter(g => g.topics.length);
}

module.exports = { lessonTopics };
