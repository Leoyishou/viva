from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入应用层用例,每个用例类通常代表用户视角的单一操作或任务。
from application.use_cases.submit_essay_use_case import SubmitEssayUseCase
from application.use_cases.get_user_essays_use_case import GetUserEssaysUseCase

# 导入接口层控制器
from interfaces.api.auth_controller import router as auth_router
from interfaces.api.essay_controller import router as essay_router

# 导入领域层服务
from domain.services.essay_processing_service import EssayProcessingService

# 导入基础设施层服务
from infrastructure.repositories.sentence_repository import SentenceRepository
from infrastructure.text_processing.segmentation_service import SegmentationService
from infrastructure.repositories.essay_repository import EssayRepository
from infrastructure.repositories.active_mapping_repository import ActiveMappingRepository
from infrastructure.logging.logging_config import setup_logging


# 设置日志
logger = setup_logging()

app = FastAPI(title="Vocabulary Management API")

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 修改依赖注入配置
def configure_dependencies():
    segmentation_service = SegmentationService()
    sentence_repository = SentenceRepository()
    essay_repository = EssayRepository()
    active_mapping_repository = ActiveMappingRepository()
    essay_processing_service = EssayProcessingService(segmentation_service, sentence_repository, active_mapping_repository)
    
    # 注册 SubmitEssayUseCase 依赖
    app.dependency_overrides[SubmitEssayUseCase] = lambda: SubmitEssayUseCase(
        essay_processing_service,
        essay_repository
    )
    
    # 将 GetUserEssaysUseCase 依赖移到这里
    app.dependency_overrides[GetUserEssaysUseCase] = lambda: GetUserEssaysUseCase(essay_repository)

# 注册路由
app.include_router(auth_router)
app.include_router(essay_router)
# app.include_router(word_router)
# app.include_router(anki_router)

if __name__ == "__main__":
    logger.info("Application started")
    configure_dependencies()
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)