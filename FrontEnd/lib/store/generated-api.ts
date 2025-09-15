import { api } from "./api";
export const addTagTypes = [
  "Authentication",
  "Users",
  "Clients",
  "Trainers",
  "Exercises",
  "Progress",
  "Programs",
  "Sessions",
  "Meals",
  "Notifications",
] as const;
const injectedRtkApi = api
  .enhanceEndpoints({
    addTagTypes,
  })
  .injectEndpoints({
    endpoints: (build) => ({
      healthCheckApiHealthGet: build.query<
        HealthCheckApiHealthGetApiResponse,
        HealthCheckApiHealthGetApiArg
      >({
        query: () => ({ url: `/api/health` }),
      }),
      registerApiV1AuthRegisterPost: build.mutation<
        RegisterApiV1AuthRegisterPostApiResponse,
        RegisterApiV1AuthRegisterPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/auth/register`,
          method: "POST",
          body: queryArg.registerRequest,
        }),
        invalidatesTags: ["Authentication"],
      }),
      loginApiV1AuthLoginPost: build.mutation<
        LoginApiV1AuthLoginPostApiResponse,
        LoginApiV1AuthLoginPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/auth/login`,
          method: "POST",
          body: queryArg.loginRequest,
        }),
        invalidatesTags: ["Authentication"],
      }),
      refreshTokenApiV1AuthRefreshPost: build.mutation<
        RefreshTokenApiV1AuthRefreshPostApiResponse,
        RefreshTokenApiV1AuthRefreshPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/auth/refresh`,
          method: "POST",
          body: queryArg.refreshTokenRequest,
        }),
        invalidatesTags: ["Authentication"],
      }),
      getProfileApiV1AuthMeGet: build.query<
        GetProfileApiV1AuthMeGetApiResponse,
        GetProfileApiV1AuthMeGetApiArg
      >({
        query: () => ({ url: `/api/v1/auth/me` }),
        providesTags: ["Authentication"],
      }),
      updateProfileApiV1AuthMePut: build.mutation<
        UpdateProfileApiV1AuthMePutApiResponse,
        UpdateProfileApiV1AuthMePutApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/auth/me`,
          method: "PUT",
          body: queryArg.updateProfile,
        }),
        invalidatesTags: ["Authentication"],
      }),
      changePasswordApiV1AuthChangePasswordPost: build.mutation<
        ChangePasswordApiV1AuthChangePasswordPostApiResponse,
        ChangePasswordApiV1AuthChangePasswordPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/auth/change-password`,
          method: "POST",
          body: queryArg.passwordChangeRequest,
        }),
        invalidatesTags: ["Authentication"],
      }),
      listUsersApiV1UsersGet: build.query<
        ListUsersApiV1UsersGetApiResponse,
        ListUsersApiV1UsersGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/users/`,
          params: {
            skip: queryArg.skip,
            limit: queryArg.limit,
          },
        }),
        providesTags: ["Users"],
      }),
      getUserApiV1UsersUserIdGet: build.query<
        GetUserApiV1UsersUserIdGetApiResponse,
        GetUserApiV1UsersUserIdGetApiArg
      >({
        query: (queryArg) => ({ url: `/api/v1/users/${queryArg.userId}` }),
        providesTags: ["Users"],
      }),
      listClientsApiV1ClientsGet: build.query<
        ListClientsApiV1ClientsGetApiResponse,
        ListClientsApiV1ClientsGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/clients/`,
          params: {
            skip: queryArg.skip,
            limit: queryArg.limit,
          },
        }),
        providesTags: ["Clients"],
      }),
      createClientProfileApiV1ClientsPost: build.mutation<
        CreateClientProfileApiV1ClientsPostApiResponse,
        CreateClientProfileApiV1ClientsPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/clients/`,
          method: "POST",
          body: queryArg.clientCreate,
        }),
        invalidatesTags: ["Clients"],
      }),
      getMyClientProfileApiV1ClientsMeGet: build.query<
        GetMyClientProfileApiV1ClientsMeGetApiResponse,
        GetMyClientProfileApiV1ClientsMeGetApiArg
      >({
        query: () => ({ url: `/api/v1/clients/me` }),
        providesTags: ["Clients"],
      }),
      updateMyClientProfileApiV1ClientsMePut: build.mutation<
        UpdateMyClientProfileApiV1ClientsMePutApiResponse,
        UpdateMyClientProfileApiV1ClientsMePutApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/clients/me`,
          method: "PUT",
          body: queryArg.clientUpdate,
        }),
        invalidatesTags: ["Clients"],
      }),
      clientPinLoginApiV1ClientsPinAccessPost: build.mutation<
        ClientPinLoginApiV1ClientsPinAccessPostApiResponse,
        ClientPinLoginApiV1ClientsPinAccessPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/clients/pin-access`,
          method: "POST",
          body: queryArg.clientPinAccess,
        }),
        invalidatesTags: ["Clients"],
      }),
      updateProfileViaPinApiV1ClientsPinProfileClientIdPut: build.mutation<
        UpdateProfileViaPinApiV1ClientsPinProfileClientIdPutApiResponse,
        UpdateProfileViaPinApiV1ClientsPinProfileClientIdPutApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/clients/pin-profile/${queryArg.clientId}`,
          method: "PUT",
          body: queryArg.clientProfileUpdate,
        }),
        invalidatesTags: ["Clients"],
      }),
      getClientProfileApiV1ClientsClientIdGet: build.query<
        GetClientProfileApiV1ClientsClientIdGetApiResponse,
        GetClientProfileApiV1ClientsClientIdGetApiArg
      >({
        query: (queryArg) => ({ url: `/api/v1/clients/${queryArg.clientId}` }),
        providesTags: ["Clients"],
      }),
      updateClientProfileApiV1ClientsClientIdPut: build.mutation<
        UpdateClientProfileApiV1ClientsClientIdPutApiResponse,
        UpdateClientProfileApiV1ClientsClientIdPutApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/clients/${queryArg.clientId}`,
          method: "PUT",
          body: queryArg.clientUpdate,
        }),
        invalidatesTags: ["Clients"],
      }),
      assignTrainerToClientApiV1ClientsClientIdAssignTrainerTrainerIdPost:
        build.mutation<
          AssignTrainerToClientApiV1ClientsClientIdAssignTrainerTrainerIdPostApiResponse,
          AssignTrainerToClientApiV1ClientsClientIdAssignTrainerTrainerIdPostApiArg
        >({
          query: (queryArg) => ({
            url: `/api/v1/clients/${queryArg.clientId}/assign-trainer/${queryArg.trainerId}`,
            method: "POST",
          }),
          invalidatesTags: ["Clients"],
        }),
      regenerateClientPinApiV1ClientsClientIdRegeneratePinPost: build.mutation<
        RegenerateClientPinApiV1ClientsClientIdRegeneratePinPostApiResponse,
        RegenerateClientPinApiV1ClientsClientIdRegeneratePinPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/clients/${queryArg.clientId}/regenerate-pin`,
          method: "POST",
        }),
        invalidatesTags: ["Clients"],
      }),
      getClientStatsApiV1ClientsClientIdStatsGet: build.query<
        GetClientStatsApiV1ClientsClientIdStatsGetApiResponse,
        GetClientStatsApiV1ClientsClientIdStatsGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/clients/${queryArg.clientId}/stats`,
        }),
        providesTags: ["Clients"],
      }),
      getTrainerClientsApiV1ClientsTrainerTrainerIdClientsGet: build.query<
        GetTrainerClientsApiV1ClientsTrainerTrainerIdClientsGetApiResponse,
        GetTrainerClientsApiV1ClientsTrainerTrainerIdClientsGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/clients/trainer/${queryArg.trainerId}/clients`,
          params: {
            skip: queryArg.skip,
            limit: queryArg.limit,
          },
        }),
        providesTags: ["Clients"],
      }),
      createTrainerProfileApiV1TrainersPost: build.mutation<
        CreateTrainerProfileApiV1TrainersPostApiResponse,
        CreateTrainerProfileApiV1TrainersPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/trainers/`,
          method: "POST",
          body: queryArg.trainerCreate,
        }),
        invalidatesTags: ["Trainers"],
      }),
      getAllTrainersApiV1TrainersGet: build.query<
        GetAllTrainersApiV1TrainersGetApiResponse,
        GetAllTrainersApiV1TrainersGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/trainers/`,
          params: {
            skip: queryArg.skip,
            limit: queryArg.limit,
            is_active: queryArg.isActive,
          },
        }),
        providesTags: ["Trainers"],
      }),
      searchTrainersApiV1TrainersSearchGet: build.query<
        SearchTrainersApiV1TrainersSearchGetApiResponse,
        SearchTrainersApiV1TrainersSearchGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/trainers/search`,
          params: {
            specialization: queryArg.specialization,
            location: queryArg.location,
            min_experience: queryArg.minExperience,
            skip: queryArg.skip,
            limit: queryArg.limit,
          },
        }),
        providesTags: ["Trainers"],
      }),
      getMyTrainerProfileApiV1TrainersMeGet: build.query<
        GetMyTrainerProfileApiV1TrainersMeGetApiResponse,
        GetMyTrainerProfileApiV1TrainersMeGetApiArg
      >({
        query: () => ({ url: `/api/v1/trainers/me` }),
        providesTags: ["Trainers"],
      }),
      updateMyTrainerProfileApiV1TrainersMePut: build.mutation<
        UpdateMyTrainerProfileApiV1TrainersMePutApiResponse,
        UpdateMyTrainerProfileApiV1TrainersMePutApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/trainers/me`,
          method: "PUT",
          body: queryArg.trainerUpdate,
        }),
        invalidatesTags: ["Trainers"],
      }),
      getMyDashboardApiV1TrainersMeDashboardGet: build.query<
        GetMyDashboardApiV1TrainersMeDashboardGetApiResponse,
        GetMyDashboardApiV1TrainersMeDashboardGetApiArg
      >({
        query: () => ({ url: `/api/v1/trainers/me/dashboard` }),
        providesTags: ["Trainers"],
      }),
      getMyStatsApiV1TrainersMeStatsGet: build.query<
        GetMyStatsApiV1TrainersMeStatsGetApiResponse,
        GetMyStatsApiV1TrainersMeStatsGetApiArg
      >({
        query: () => ({ url: `/api/v1/trainers/me/stats` }),
        providesTags: ["Trainers"],
      }),
      getMyCertificationsApiV1TrainersMeCertificationsGet: build.query<
        GetMyCertificationsApiV1TrainersMeCertificationsGetApiResponse,
        GetMyCertificationsApiV1TrainersMeCertificationsGetApiArg
      >({
        query: () => ({ url: `/api/v1/trainers/me/certifications` }),
        providesTags: ["Trainers"],
      }),
      addCertificationApiV1TrainersMeCertificationsPost: build.mutation<
        AddCertificationApiV1TrainersMeCertificationsPostApiResponse,
        AddCertificationApiV1TrainersMeCertificationsPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/trainers/me/certifications`,
          method: "POST",
          body: queryArg.trainerCertificationCreate,
        }),
        invalidatesTags: ["Trainers"],
      }),
      updateCertificationApiV1TrainersCertificationsCertificationIdPut:
        build.mutation<
          UpdateCertificationApiV1TrainersCertificationsCertificationIdPutApiResponse,
          UpdateCertificationApiV1TrainersCertificationsCertificationIdPutApiArg
        >({
          query: (queryArg) => ({
            url: `/api/v1/trainers/certifications/${queryArg.certificationId}`,
            method: "PUT",
            body: queryArg.trainerCertificationUpdate,
          }),
          invalidatesTags: ["Trainers"],
        }),
      getMyAvailabilityApiV1TrainersMeAvailabilityGet: build.query<
        GetMyAvailabilityApiV1TrainersMeAvailabilityGetApiResponse,
        GetMyAvailabilityApiV1TrainersMeAvailabilityGetApiArg
      >({
        query: () => ({ url: `/api/v1/trainers/me/availability` }),
        providesTags: ["Trainers"],
      }),
      setAvailabilityApiV1TrainersMeAvailabilityPost: build.mutation<
        SetAvailabilityApiV1TrainersMeAvailabilityPostApiResponse,
        SetAvailabilityApiV1TrainersMeAvailabilityPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/trainers/me/availability`,
          method: "POST",
          body: queryArg.trainerAvailabilityCreate,
        }),
        invalidatesTags: ["Trainers"],
      }),
      getTrainerProfileApiV1TrainersTrainerIdGet: build.query<
        GetTrainerProfileApiV1TrainersTrainerIdGetApiResponse,
        GetTrainerProfileApiV1TrainersTrainerIdGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/trainers/${queryArg.trainerId}`,
        }),
        providesTags: ["Trainers"],
      }),
      updateTrainerProfileApiV1TrainersTrainerIdPut: build.mutation<
        UpdateTrainerProfileApiV1TrainersTrainerIdPutApiResponse,
        UpdateTrainerProfileApiV1TrainersTrainerIdPutApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/trainers/${queryArg.trainerId}`,
          method: "PUT",
          body: queryArg.trainerUpdate,
        }),
        invalidatesTags: ["Trainers"],
      }),
      getTrainerClientsByIdApiV1TrainersTrainerIdClientsGet: build.query<
        GetTrainerClientsByIdApiV1TrainersTrainerIdClientsGetApiResponse,
        GetTrainerClientsByIdApiV1TrainersTrainerIdClientsGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/trainers/${queryArg.trainerId}/clients`,
          params: {
            skip: queryArg.skip,
            limit: queryArg.limit,
          },
        }),
        providesTags: ["Trainers"],
      }),
      getTrainerSessionsApiV1TrainersTrainerIdSessionsGet: build.query<
        GetTrainerSessionsApiV1TrainersTrainerIdSessionsGetApiResponse,
        GetTrainerSessionsApiV1TrainersTrainerIdSessionsGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/trainers/${queryArg.trainerId}/sessions`,
        }),
        providesTags: ["Trainers"],
      }),
      getTrainerStatsByIdApiV1TrainersTrainerIdStatsGet: build.query<
        GetTrainerStatsByIdApiV1TrainersTrainerIdStatsGetApiResponse,
        GetTrainerStatsByIdApiV1TrainersTrainerIdStatsGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/trainers/${queryArg.trainerId}/stats`,
        }),
        providesTags: ["Trainers"],
      }),
      getExercisesApiV1ExercisesGet: build.query<
        GetExercisesApiV1ExercisesGetApiResponse,
        GetExercisesApiV1ExercisesGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/exercises/`,
          params: {
            skip: queryArg.skip,
            limit: queryArg.limit,
            category: queryArg.category,
            exercise_type: queryArg.exerciseType,
            primary_muscle_group: queryArg.primaryMuscleGroup,
            difficulty_level: queryArg.difficultyLevel,
            equipment_needed: queryArg.equipmentNeeded,
            max_duration_minutes: queryArg.maxDurationMinutes,
            search: queryArg.search,
          },
        }),
        providesTags: ["Exercises"],
      }),
      createExerciseApiV1ExercisesPost: build.mutation<
        CreateExerciseApiV1ExercisesPostApiResponse,
        CreateExerciseApiV1ExercisesPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/exercises/`,
          method: "POST",
          body: queryArg.exerciseCreate,
        }),
        invalidatesTags: ["Exercises"],
      }),
      seedDefaultExercisesApiV1ExercisesSeedGet: build.query<
        SeedDefaultExercisesApiV1ExercisesSeedGetApiResponse,
        SeedDefaultExercisesApiV1ExercisesSeedGetApiArg
      >({
        query: () => ({ url: `/api/v1/exercises/seed` }),
        providesTags: ["Exercises"],
      }),
      searchExercisesApiV1ExercisesSearchGet: build.query<
        SearchExercisesApiV1ExercisesSearchGetApiResponse,
        SearchExercisesApiV1ExercisesSearchGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/exercises/search`,
          params: {
            search_term: queryArg.searchTerm,
            limit: queryArg.limit,
          },
        }),
        providesTags: ["Exercises"],
      }),
      getPopularExercisesApiV1ExercisesPopularGet: build.query<
        GetPopularExercisesApiV1ExercisesPopularGetApiResponse,
        GetPopularExercisesApiV1ExercisesPopularGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/exercises/popular`,
          params: {
            limit: queryArg.limit,
          },
        }),
        providesTags: ["Exercises"],
      }),
      getExerciseCategoriesApiV1ExercisesCategoriesGet: build.query<
        GetExerciseCategoriesApiV1ExercisesCategoriesGetApiResponse,
        GetExerciseCategoriesApiV1ExercisesCategoriesGetApiArg
      >({
        query: () => ({ url: `/api/v1/exercises/categories` }),
        providesTags: ["Exercises"],
      }),
      getMuscleGroupsApiV1ExercisesMuscleGroupsGet: build.query<
        GetMuscleGroupsApiV1ExercisesMuscleGroupsGetApiResponse,
        GetMuscleGroupsApiV1ExercisesMuscleGroupsGetApiArg
      >({
        query: () => ({ url: `/api/v1/exercises/muscle-groups` }),
        providesTags: ["Exercises"],
      }),
      getExerciseTypesApiV1ExercisesTypesGet: build.query<
        GetExerciseTypesApiV1ExercisesTypesGetApiResponse,
        GetExerciseTypesApiV1ExercisesTypesGetApiArg
      >({
        query: () => ({ url: `/api/v1/exercises/types` }),
        providesTags: ["Exercises"],
      }),
      getExercisesByMuscleGroupApiV1ExercisesByMuscleMuscleGroupGet:
        build.query<
          GetExercisesByMuscleGroupApiV1ExercisesByMuscleMuscleGroupGetApiResponse,
          GetExercisesByMuscleGroupApiV1ExercisesByMuscleMuscleGroupGetApiArg
        >({
          query: (queryArg) => ({
            url: `/api/v1/exercises/by-muscle/${queryArg.muscleGroup}`,
            params: {
              include_secondary: queryArg.includeSecondary,
            },
          }),
          providesTags: ["Exercises"],
        }),
      getExercisesByEquipmentApiV1ExercisesByEquipmentEquipmentGet: build.query<
        GetExercisesByEquipmentApiV1ExercisesByEquipmentEquipmentGetApiResponse,
        GetExercisesByEquipmentApiV1ExercisesByEquipmentEquipmentGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/exercises/by-equipment/${queryArg.equipment}`,
        }),
        providesTags: ["Exercises"],
      }),
      getBodyweightExercisesApiV1ExercisesBodyweightGet: build.query<
        GetBodyweightExercisesApiV1ExercisesBodyweightGetApiResponse,
        GetBodyweightExercisesApiV1ExercisesBodyweightGetApiArg
      >({
        query: () => ({ url: `/api/v1/exercises/bodyweight` }),
        providesTags: ["Exercises"],
      }),
      getExerciseApiV1ExercisesExerciseIdGet: build.query<
        GetExerciseApiV1ExercisesExerciseIdGetApiResponse,
        GetExerciseApiV1ExercisesExerciseIdGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/exercises/${queryArg.exerciseId}`,
        }),
        providesTags: ["Exercises"],
      }),
      updateExerciseApiV1ExercisesExerciseIdPut: build.mutation<
        UpdateExerciseApiV1ExercisesExerciseIdPutApiResponse,
        UpdateExerciseApiV1ExercisesExerciseIdPutApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/exercises/${queryArg.exerciseId}`,
          method: "PUT",
          body: queryArg.exerciseUpdate,
        }),
        invalidatesTags: ["Exercises"],
      }),
      deleteExerciseApiV1ExercisesExerciseIdDelete: build.mutation<
        DeleteExerciseApiV1ExercisesExerciseIdDeleteApiResponse,
        DeleteExerciseApiV1ExercisesExerciseIdDeleteApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/exercises/${queryArg.exerciseId}`,
          method: "DELETE",
        }),
        invalidatesTags: ["Exercises"],
      }),
      createProgressLogApiV1ProgressPost: build.mutation<
        CreateProgressLogApiV1ProgressPostApiResponse,
        CreateProgressLogApiV1ProgressPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/progress/`,
          method: "POST",
          body: queryArg.progressLogCreate,
        }),
        invalidatesTags: ["Progress"],
      }),
      getClientProgressLogsApiV1ProgressClientClientIdGet: build.query<
        GetClientProgressLogsApiV1ProgressClientClientIdGetApiResponse,
        GetClientProgressLogsApiV1ProgressClientClientIdGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/progress/client/${queryArg.clientId}`,
          params: {
            skip: queryArg.skip,
            limit: queryArg.limit,
            log_type: queryArg.logType,
            exercise_id: queryArg.exerciseId,
            start_date: queryArg.startDate,
            end_date: queryArg.endDate,
          },
        }),
        providesTags: ["Progress"],
      }),
      getClientProgressStatsApiV1ProgressClientClientIdStatsGet: build.query<
        GetClientProgressStatsApiV1ProgressClientClientIdStatsGetApiResponse,
        GetClientProgressStatsApiV1ProgressClientClientIdStatsGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/progress/client/${queryArg.clientId}/stats`,
        }),
        providesTags: ["Progress"],
      }),
      getProgressLogApiV1ProgressLogIdGet: build.query<
        GetProgressLogApiV1ProgressLogIdGetApiResponse,
        GetProgressLogApiV1ProgressLogIdGetApiArg
      >({
        query: (queryArg) => ({ url: `/api/v1/progress/${queryArg.logId}` }),
        providesTags: ["Progress"],
      }),
      updateProgressLogApiV1ProgressLogIdPut: build.mutation<
        UpdateProgressLogApiV1ProgressLogIdPutApiResponse,
        UpdateProgressLogApiV1ProgressLogIdPutApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/progress/${queryArg.logId}`,
          method: "PUT",
          body: queryArg.progressLogUpdate,
        }),
        invalidatesTags: ["Progress"],
      }),
      deleteProgressLogApiV1ProgressLogIdDelete: build.mutation<
        DeleteProgressLogApiV1ProgressLogIdDeleteApiResponse,
        DeleteProgressLogApiV1ProgressLogIdDeleteApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/progress/${queryArg.logId}`,
          method: "DELETE",
        }),
        invalidatesTags: ["Progress"],
      }),
      createProgramApiV1ProgramsPost: build.mutation<
        CreateProgramApiV1ProgramsPostApiResponse,
        CreateProgramApiV1ProgramsPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/programs/`,
          method: "POST",
          body: queryArg.programCreate,
        }),
        invalidatesTags: ["Programs"],
      }),
      getProgramsApiV1ProgramsGet: build.query<
        GetProgramsApiV1ProgramsGetApiResponse,
        GetProgramsApiV1ProgramsGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/programs/`,
          params: {
            skip: queryArg.skip,
            limit: queryArg.limit,
            status: queryArg.status,
            difficulty_level: queryArg.difficultyLevel,
            trainer_id: queryArg.trainerId,
            duration_weeks_min: queryArg.durationWeeksMin,
            duration_weeks_max: queryArg.durationWeeksMax,
            search: queryArg.search,
          },
        }),
        providesTags: ["Programs"],
      }),
      getPopularProgramsApiV1ProgramsPopularGet: build.query<
        GetPopularProgramsApiV1ProgramsPopularGetApiResponse,
        GetPopularProgramsApiV1ProgramsPopularGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/programs/popular`,
          params: {
            limit: queryArg.limit,
          },
        }),
        providesTags: ["Programs"],
      }),
      searchProgramsApiV1ProgramsSearchGet: build.query<
        SearchProgramsApiV1ProgramsSearchGetApiResponse,
        SearchProgramsApiV1ProgramsSearchGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/programs/search`,
          params: {
            search_term: queryArg.searchTerm,
            limit: queryArg.limit,
          },
        }),
        providesTags: ["Programs"],
      }),
      getTrainerProgramsApiV1ProgramsTrainerTrainerIdGet: build.query<
        GetTrainerProgramsApiV1ProgramsTrainerTrainerIdGetApiResponse,
        GetTrainerProgramsApiV1ProgramsTrainerTrainerIdGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/programs/trainer/${queryArg.trainerId}`,
        }),
        providesTags: ["Programs"],
      }),
      getProgramApiV1ProgramsProgramIdGet: build.query<
        GetProgramApiV1ProgramsProgramIdGetApiResponse,
        GetProgramApiV1ProgramsProgramIdGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/programs/${queryArg.programId}`,
        }),
        providesTags: ["Programs"],
      }),
      updateProgramApiV1ProgramsProgramIdPut: build.mutation<
        UpdateProgramApiV1ProgramsProgramIdPutApiResponse,
        UpdateProgramApiV1ProgramsProgramIdPutApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/programs/${queryArg.programId}`,
          method: "PUT",
          body: queryArg.programUpdate,
        }),
        invalidatesTags: ["Programs"],
      }),
      deleteProgramApiV1ProgramsProgramIdDelete: build.mutation<
        DeleteProgramApiV1ProgramsProgramIdDeleteApiResponse,
        DeleteProgramApiV1ProgramsProgramIdDeleteApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/programs/${queryArg.programId}`,
          method: "DELETE",
        }),
        invalidatesTags: ["Programs"],
      }),
      addExerciseToProgramApiV1ProgramsProgramIdExercisesPost: build.mutation<
        AddExerciseToProgramApiV1ProgramsProgramIdExercisesPostApiResponse,
        AddExerciseToProgramApiV1ProgramsProgramIdExercisesPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/programs/${queryArg.programId}/exercises`,
          method: "POST",
          body: queryArg.programExerciseCreate,
        }),
        invalidatesTags: ["Programs"],
      }),
      getProgramExercisesApiV1ProgramsProgramIdExercisesGet: build.query<
        GetProgramExercisesApiV1ProgramsProgramIdExercisesGetApiResponse,
        GetProgramExercisesApiV1ProgramsProgramIdExercisesGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/programs/${queryArg.programId}/exercises`,
        }),
        providesTags: ["Programs"],
      }),
      createSessionBookingApiV1SessionsPost: build.mutation<
        CreateSessionBookingApiV1SessionsPostApiResponse,
        CreateSessionBookingApiV1SessionsPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/sessions/`,
          method: "POST",
          body: queryArg.sessionBookingCreate,
        }),
        invalidatesTags: ["Sessions"],
      }),
      getSessionBookingsApiV1SessionsGet: build.query<
        GetSessionBookingsApiV1SessionsGetApiResponse,
        GetSessionBookingsApiV1SessionsGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/sessions/`,
          params: {
            skip: queryArg.skip,
            limit: queryArg.limit,
            client_id: queryArg.clientId,
            trainer_id: queryArg.trainerId,
            status: queryArg.status,
            start_date: queryArg.startDate,
            end_date: queryArg.endDate,
            session_type: queryArg.sessionType,
          },
        }),
        providesTags: ["Sessions"],
      }),
      getTrainerScheduleApiV1SessionsTrainerTrainerIdScheduleGet: build.query<
        GetTrainerScheduleApiV1SessionsTrainerTrainerIdScheduleGetApiResponse,
        GetTrainerScheduleApiV1SessionsTrainerTrainerIdScheduleGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/sessions/trainer/${queryArg.trainerId}/schedule`,
          params: {
            start_date: queryArg.startDate,
            end_date: queryArg.endDate,
          },
        }),
        providesTags: ["Sessions"],
      }),
      getAvailableTimeSlotsApiV1SessionsTrainerTrainerIdAvailabilityDateGet:
        build.query<
          GetAvailableTimeSlotsApiV1SessionsTrainerTrainerIdAvailabilityDateGetApiResponse,
          GetAvailableTimeSlotsApiV1SessionsTrainerTrainerIdAvailabilityDateGetApiArg
        >({
          query: (queryArg) => ({
            url: `/api/v1/sessions/trainer/${queryArg.trainerId}/availability/${queryArg.date}`,
            params: {
              duration_minutes: queryArg.durationMinutes,
            },
          }),
          providesTags: ["Sessions"],
        }),
      getClientSessionsApiV1SessionsClientClientIdSessionsGet: build.query<
        GetClientSessionsApiV1SessionsClientClientIdSessionsGetApiResponse,
        GetClientSessionsApiV1SessionsClientClientIdSessionsGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/sessions/client/${queryArg.clientId}/sessions`,
          params: {
            start_date: queryArg.startDate,
            end_date: queryArg.endDate,
          },
        }),
        providesTags: ["Sessions"],
      }),
      getSessionBookingApiV1SessionsBookingIdGet: build.query<
        GetSessionBookingApiV1SessionsBookingIdGetApiResponse,
        GetSessionBookingApiV1SessionsBookingIdGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/sessions/${queryArg.bookingId}`,
        }),
        providesTags: ["Sessions"],
      }),
      updateSessionBookingApiV1SessionsBookingIdPut: build.mutation<
        UpdateSessionBookingApiV1SessionsBookingIdPutApiResponse,
        UpdateSessionBookingApiV1SessionsBookingIdPutApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/sessions/${queryArg.bookingId}`,
          method: "PUT",
          body: queryArg.sessionBookingUpdate,
        }),
        invalidatesTags: ["Sessions"],
      }),
      cancelSessionBookingApiV1SessionsBookingIdCancelPost: build.mutation<
        CancelSessionBookingApiV1SessionsBookingIdCancelPostApiResponse,
        CancelSessionBookingApiV1SessionsBookingIdCancelPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/sessions/${queryArg.bookingId}/cancel`,
          method: "POST",
          params: {
            reason: queryArg.reason,
          },
        }),
        invalidatesTags: ["Sessions"],
      }),
      confirmSessionBookingApiV1SessionsBookingIdConfirmPost: build.mutation<
        ConfirmSessionBookingApiV1SessionsBookingIdConfirmPostApiResponse,
        ConfirmSessionBookingApiV1SessionsBookingIdConfirmPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/sessions/${queryArg.bookingId}/confirm`,
          method: "POST",
        }),
        invalidatesTags: ["Sessions"],
      }),
      completeSessionBookingApiV1SessionsBookingIdCompletePost: build.mutation<
        CompleteSessionBookingApiV1SessionsBookingIdCompletePostApiResponse,
        CompleteSessionBookingApiV1SessionsBookingIdCompletePostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/sessions/${queryArg.bookingId}/complete`,
          method: "POST",
          params: {
            session_notes: queryArg.sessionNotes,
          },
        }),
        invalidatesTags: ["Sessions"],
      }),
      createMealPlanApiV1MealsPost: build.mutation<
        CreateMealPlanApiV1MealsPostApiResponse,
        CreateMealPlanApiV1MealsPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/meals/`,
          method: "POST",
          body: queryArg.mealPlanCreate,
        }),
        invalidatesTags: ["Meals"],
      }),
      getMealPlansApiV1MealsGet: build.query<
        GetMealPlansApiV1MealsGetApiResponse,
        GetMealPlansApiV1MealsGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/meals/`,
          params: {
            skip: queryArg.skip,
            limit: queryArg.limit,
            client_id: queryArg.clientId,
            diet_type: queryArg.dietType,
            target_calories_min: queryArg.targetCaloriesMin,
            target_calories_max: queryArg.targetCaloriesMax,
            search: queryArg.search,
          },
        }),
        providesTags: ["Meals"],
      }),
      searchMealPlansApiV1MealsSearchGet: build.query<
        SearchMealPlansApiV1MealsSearchGetApiResponse,
        SearchMealPlansApiV1MealsSearchGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/meals/search`,
          params: {
            search_term: queryArg.searchTerm,
            limit: queryArg.limit,
          },
        }),
        providesTags: ["Meals"],
      }),
      getClientActiveMealPlansApiV1MealsClientClientIdActiveGet: build.query<
        GetClientActiveMealPlansApiV1MealsClientClientIdActiveGetApiResponse,
        GetClientActiveMealPlansApiV1MealsClientClientIdActiveGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/meals/client/${queryArg.clientId}/active`,
        }),
        providesTags: ["Meals"],
      }),
      getMealPlanApiV1MealsMealPlanIdGet: build.query<
        GetMealPlanApiV1MealsMealPlanIdGetApiResponse,
        GetMealPlanApiV1MealsMealPlanIdGetApiArg
      >({
        query: (queryArg) => ({ url: `/api/v1/meals/${queryArg.mealPlanId}` }),
        providesTags: ["Meals"],
      }),
      updateMealPlanApiV1MealsMealPlanIdPut: build.mutation<
        UpdateMealPlanApiV1MealsMealPlanIdPutApiResponse,
        UpdateMealPlanApiV1MealsMealPlanIdPutApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/meals/${queryArg.mealPlanId}`,
          method: "PUT",
          body: queryArg.mealPlanUpdate,
        }),
        invalidatesTags: ["Meals"],
      }),
      deleteMealPlanApiV1MealsMealPlanIdDelete: build.mutation<
        DeleteMealPlanApiV1MealsMealPlanIdDeleteApiResponse,
        DeleteMealPlanApiV1MealsMealPlanIdDeleteApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/meals/${queryArg.mealPlanId}`,
          method: "DELETE",
        }),
        invalidatesTags: ["Meals"],
      }),
      addRecipeToMealPlanApiV1MealsMealPlanIdRecipesPost: build.mutation<
        AddRecipeToMealPlanApiV1MealsMealPlanIdRecipesPostApiResponse,
        AddRecipeToMealPlanApiV1MealsMealPlanIdRecipesPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/meals/${queryArg.mealPlanId}/recipes`,
          method: "POST",
          body: queryArg.mealPlanRecipeCreate,
        }),
        invalidatesTags: ["Meals"],
      }),
      getMealPlanRecipesApiV1MealsMealPlanIdRecipesGet: build.query<
        GetMealPlanRecipesApiV1MealsMealPlanIdRecipesGetApiResponse,
        GetMealPlanRecipesApiV1MealsMealPlanIdRecipesGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/meals/${queryArg.mealPlanId}/recipes`,
        }),
        providesTags: ["Meals"],
      }),
      getDailyMealPlanApiV1MealsMealPlanIdDayDayNumberGet: build.query<
        GetDailyMealPlanApiV1MealsMealPlanIdDayDayNumberGetApiResponse,
        GetDailyMealPlanApiV1MealsMealPlanIdDayDayNumberGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/meals/${queryArg.mealPlanId}/day/${queryArg.dayNumber}`,
        }),
        providesTags: ["Meals"],
      }),
      getMealPlanNutritionApiV1MealsMealPlanIdNutritionGet: build.query<
        GetMealPlanNutritionApiV1MealsMealPlanIdNutritionGetApiResponse,
        GetMealPlanNutritionApiV1MealsMealPlanIdNutritionGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/meals/${queryArg.mealPlanId}/nutrition`,
        }),
        providesTags: ["Meals"],
      }),
      getWeeklyMealPlanApiV1MealsMealPlanIdWeeklyGet: build.query<
        GetWeeklyMealPlanApiV1MealsMealPlanIdWeeklyGetApiResponse,
        GetWeeklyMealPlanApiV1MealsMealPlanIdWeeklyGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/meals/${queryArg.mealPlanId}/weekly`,
        }),
        providesTags: ["Meals"],
      }),
      duplicateMealPlanApiV1MealsMealPlanIdDuplicatePost: build.mutation<
        DuplicateMealPlanApiV1MealsMealPlanIdDuplicatePostApiResponse,
        DuplicateMealPlanApiV1MealsMealPlanIdDuplicatePostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/meals/${queryArg.mealPlanId}/duplicate`,
          method: "POST",
          params: {
            new_name: queryArg.newName,
            client_id: queryArg.clientId,
          },
        }),
        invalidatesTags: ["Meals"],
      }),
      createNotificationTemplateApiV1NotificationsTemplatesPost: build.mutation<
        CreateNotificationTemplateApiV1NotificationsTemplatesPostApiResponse,
        CreateNotificationTemplateApiV1NotificationsTemplatesPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/notifications/templates`,
          method: "POST",
          body: queryArg.notificationTemplateCreate,
        }),
        invalidatesTags: ["Notifications"],
      }),
      getNotificationTemplatesApiV1NotificationsTemplatesGet: build.query<
        GetNotificationTemplatesApiV1NotificationsTemplatesGetApiResponse,
        GetNotificationTemplatesApiV1NotificationsTemplatesGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/notifications/templates`,
          params: {
            skip: queryArg.skip,
            limit: queryArg.limit,
          },
        }),
        providesTags: ["Notifications"],
      }),
      getNotificationTemplateApiV1NotificationsTemplatesTemplateIdGet:
        build.query<
          GetNotificationTemplateApiV1NotificationsTemplatesTemplateIdGetApiResponse,
          GetNotificationTemplateApiV1NotificationsTemplatesTemplateIdGetApiArg
        >({
          query: (queryArg) => ({
            url: `/api/v1/notifications/templates/${queryArg.templateId}`,
          }),
          providesTags: ["Notifications"],
        }),
      getMyNotificationPreferencesApiV1NotificationsPreferencesGet: build.query<
        GetMyNotificationPreferencesApiV1NotificationsPreferencesGetApiResponse,
        GetMyNotificationPreferencesApiV1NotificationsPreferencesGetApiArg
      >({
        query: () => ({ url: `/api/v1/notifications/preferences` }),
        providesTags: ["Notifications"],
      }),
      updateMyNotificationPreferencesApiV1NotificationsPreferencesPut:
        build.mutation<
          UpdateMyNotificationPreferencesApiV1NotificationsPreferencesPutApiResponse,
          UpdateMyNotificationPreferencesApiV1NotificationsPreferencesPutApiArg
        >({
          query: (queryArg) => ({
            url: `/api/v1/notifications/preferences`,
            method: "PUT",
            body: queryArg.notificationPreferencesUpdate,
          }),
          invalidatesTags: ["Notifications"],
        }),
      getUserNotificationPreferencesApiV1NotificationsPreferencesUserIdGet:
        build.query<
          GetUserNotificationPreferencesApiV1NotificationsPreferencesUserIdGetApiResponse,
          GetUserNotificationPreferencesApiV1NotificationsPreferencesUserIdGetApiArg
        >({
          query: (queryArg) => ({
            url: `/api/v1/notifications/preferences/${queryArg.userId}`,
          }),
          providesTags: ["Notifications"],
        }),
      sendNotificationApiV1NotificationsSendPost: build.mutation<
        SendNotificationApiV1NotificationsSendPostApiResponse,
        SendNotificationApiV1NotificationsSendPostApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/notifications/send`,
          method: "POST",
          body: queryArg.sendNotificationRequest,
        }),
        invalidatesTags: ["Notifications"],
      }),
      getMyNotificationsApiV1NotificationsGet: build.query<
        GetMyNotificationsApiV1NotificationsGetApiResponse,
        GetMyNotificationsApiV1NotificationsGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/notifications/`,
          params: {
            skip: queryArg.skip,
            limit: queryArg.limit,
            category: queryArg.category,
            unread_only: queryArg.unreadOnly,
          },
        }),
        providesTags: ["Notifications"],
      }),
      getAllNotificationsApiV1NotificationsAllGet: build.query<
        GetAllNotificationsApiV1NotificationsAllGetApiResponse,
        GetAllNotificationsApiV1NotificationsAllGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/notifications/all`,
          params: {
            skip: queryArg.skip,
            limit: queryArg.limit,
            user_id: queryArg.userId,
            category: queryArg.category,
            status: queryArg.status,
          },
        }),
        providesTags: ["Notifications"],
      }),
      markNotificationReadApiV1NotificationsNotificationIdReadPut:
        build.mutation<
          MarkNotificationReadApiV1NotificationsNotificationIdReadPutApiResponse,
          MarkNotificationReadApiV1NotificationsNotificationIdReadPutApiArg
        >({
          query: (queryArg) => ({
            url: `/api/v1/notifications/${queryArg.notificationId}/read`,
            method: "PUT",
          }),
          invalidatesTags: ["Notifications"],
        }),
      getNotificationStatsApiV1NotificationsStatsGet: build.query<
        GetNotificationStatsApiV1NotificationsStatsGetApiResponse,
        GetNotificationStatsApiV1NotificationsStatsGetApiArg
      >({
        query: (queryArg) => ({
          url: `/api/v1/notifications/stats`,
          params: {
            user_id: queryArg.userId,
          },
        }),
        providesTags: ["Notifications"],
      }),
      healthCheckHealthGet: build.query<
        HealthCheckHealthGetApiResponse,
        HealthCheckHealthGetApiArg
      >({
        query: () => ({ url: `/health` }),
      }),
      rootGet: build.query<RootGetApiResponse, RootGetApiArg>({
        query: () => ({ url: `/` }),
      }),
    }),
    overrideExisting: false,
  });
export { injectedRtkApi as generatedApi };
export type HealthCheckApiHealthGetApiResponse =
  /** status 200 Successful Response */ any;
export type HealthCheckApiHealthGetApiArg = void;
export type RegisterApiV1AuthRegisterPostApiResponse =
  /** status 201 Successful Response */ AuthResponse;
export type RegisterApiV1AuthRegisterPostApiArg = {
  registerRequest: RegisterRequest;
};
export type LoginApiV1AuthLoginPostApiResponse =
  /** status 200 Successful Response */ AuthResponse;
export type LoginApiV1AuthLoginPostApiArg = {
  loginRequest: LoginRequest;
};
export type RefreshTokenApiV1AuthRefreshPostApiResponse =
  /** status 200 Successful Response */ {
    [key: string]: any;
  };
export type RefreshTokenApiV1AuthRefreshPostApiArg = {
  refreshTokenRequest: RefreshTokenRequest;
};
export type GetProfileApiV1AuthMeGetApiResponse =
  /** status 200 Successful Response */ UserProfile;
export type GetProfileApiV1AuthMeGetApiArg = void;
export type UpdateProfileApiV1AuthMePutApiResponse =
  /** status 200 Successful Response */ UserProfile;
export type UpdateProfileApiV1AuthMePutApiArg = {
  updateProfile: UpdateProfile;
};
export type ChangePasswordApiV1AuthChangePasswordPostApiResponse =
  /** status 200 Successful Response */ any;
export type ChangePasswordApiV1AuthChangePasswordPostApiArg = {
  passwordChangeRequest: PasswordChangeRequest;
};
export type ListUsersApiV1UsersGetApiResponse =
  /** status 200 Successful Response */ UserListResponse[];
export type ListUsersApiV1UsersGetApiArg = {
  skip?: number;
  limit?: number;
};
export type GetUserApiV1UsersUserIdGetApiResponse =
  /** status 200 Successful Response */ UserResponse;
export type GetUserApiV1UsersUserIdGetApiArg = {
  userId: number;
};
export type ListClientsApiV1ClientsGetApiResponse =
  /** status 200 Successful Response */ ClientResponse[];
export type ListClientsApiV1ClientsGetApiArg = {
  /** Number of clients to skip */
  skip?: number;
  /** Number of clients to return */
  limit?: number;
};
export type CreateClientProfileApiV1ClientsPostApiResponse =
  /** status 200 Successful Response */ ClientResponse;
export type CreateClientProfileApiV1ClientsPostApiArg = {
  clientCreate: ClientCreate;
};
export type GetMyClientProfileApiV1ClientsMeGetApiResponse =
  /** status 200 Successful Response */ ClientResponse;
export type GetMyClientProfileApiV1ClientsMeGetApiArg = void;
export type UpdateMyClientProfileApiV1ClientsMePutApiResponse =
  /** status 200 Successful Response */ ClientResponse;
export type UpdateMyClientProfileApiV1ClientsMePutApiArg = {
  clientUpdate: ClientUpdate;
};
export type ClientPinLoginApiV1ClientsPinAccessPostApiResponse =
  /** status 200 Successful Response */ ClientPinLogin;
export type ClientPinLoginApiV1ClientsPinAccessPostApiArg = {
  clientPinAccess: ClientPinAccess;
};
export type UpdateProfileViaPinApiV1ClientsPinProfileClientIdPutApiResponse =
  /** status 200 Successful Response */ ClientResponse;
export type UpdateProfileViaPinApiV1ClientsPinProfileClientIdPutApiArg = {
  clientId: number;
  clientProfileUpdate: ClientProfileUpdate;
};
export type GetClientProfileApiV1ClientsClientIdGetApiResponse =
  /** status 200 Successful Response */ ClientResponse;
export type GetClientProfileApiV1ClientsClientIdGetApiArg = {
  clientId: number;
};
export type UpdateClientProfileApiV1ClientsClientIdPutApiResponse =
  /** status 200 Successful Response */ ClientResponse;
export type UpdateClientProfileApiV1ClientsClientIdPutApiArg = {
  clientId: number;
  clientUpdate: ClientUpdate;
};
export type AssignTrainerToClientApiV1ClientsClientIdAssignTrainerTrainerIdPostApiResponse =
  /** status 200 Successful Response */ any;
export type AssignTrainerToClientApiV1ClientsClientIdAssignTrainerTrainerIdPostApiArg =
  {
    clientId: number;
    trainerId: number;
  };
export type RegenerateClientPinApiV1ClientsClientIdRegeneratePinPostApiResponse =
  /** status 200 Successful Response */ any;
export type RegenerateClientPinApiV1ClientsClientIdRegeneratePinPostApiArg = {
  clientId: number;
};
export type GetClientStatsApiV1ClientsClientIdStatsGetApiResponse =
  /** status 200 Successful Response */ ClientStats;
export type GetClientStatsApiV1ClientsClientIdStatsGetApiArg = {
  clientId: number;
};
export type GetTrainerClientsApiV1ClientsTrainerTrainerIdClientsGetApiResponse =
  /** status 200 Successful Response */ ClientResponse[];
export type GetTrainerClientsApiV1ClientsTrainerTrainerIdClientsGetApiArg = {
  trainerId: number;
  skip?: number;
  limit?: number;
};
export type CreateTrainerProfileApiV1TrainersPostApiResponse =
  /** status 200 Successful Response */ TrainerResponse;
export type CreateTrainerProfileApiV1TrainersPostApiArg = {
  trainerCreate: TrainerCreate;
};
export type GetAllTrainersApiV1TrainersGetApiResponse =
  /** status 200 Successful Response */ TrainerResponse[];
export type GetAllTrainersApiV1TrainersGetApiArg = {
  skip?: number;
  limit?: number;
  isActive?: boolean | null;
};
export type SearchTrainersApiV1TrainersSearchGetApiResponse =
  /** status 200 Successful Response */ TrainerResponse[];
export type SearchTrainersApiV1TrainersSearchGetApiArg = {
  specialization?: string | null;
  location?: string | null;
  minExperience?: number | null;
  skip?: number;
  limit?: number;
};
export type GetMyTrainerProfileApiV1TrainersMeGetApiResponse =
  /** status 200 Successful Response */ TrainerResponse;
export type GetMyTrainerProfileApiV1TrainersMeGetApiArg = void;
export type UpdateMyTrainerProfileApiV1TrainersMePutApiResponse =
  /** status 200 Successful Response */ TrainerResponse;
export type UpdateMyTrainerProfileApiV1TrainersMePutApiArg = {
  trainerUpdate: TrainerUpdate;
};
export type GetMyDashboardApiV1TrainersMeDashboardGetApiResponse =
  /** status 200 Successful Response */ TrainerDashboard;
export type GetMyDashboardApiV1TrainersMeDashboardGetApiArg = void;
export type GetMyStatsApiV1TrainersMeStatsGetApiResponse =
  /** status 200 Successful Response */ TrainerStats;
export type GetMyStatsApiV1TrainersMeStatsGetApiArg = void;
export type GetMyCertificationsApiV1TrainersMeCertificationsGetApiResponse =
  /** status 200 Successful Response */ any;
export type GetMyCertificationsApiV1TrainersMeCertificationsGetApiArg = void;
export type AddCertificationApiV1TrainersMeCertificationsPostApiResponse =
  /** status 200 Successful Response */ any;
export type AddCertificationApiV1TrainersMeCertificationsPostApiArg = {
  trainerCertificationCreate: TrainerCertificationCreate;
};
export type UpdateCertificationApiV1TrainersCertificationsCertificationIdPutApiResponse =
  /** status 200 Successful Response */ any;
export type UpdateCertificationApiV1TrainersCertificationsCertificationIdPutApiArg =
  {
    certificationId: number;
    trainerCertificationUpdate: TrainerCertificationUpdate;
  };
export type GetMyAvailabilityApiV1TrainersMeAvailabilityGetApiResponse =
  /** status 200 Successful Response */ any;
export type GetMyAvailabilityApiV1TrainersMeAvailabilityGetApiArg = void;
export type SetAvailabilityApiV1TrainersMeAvailabilityPostApiResponse =
  /** status 200 Successful Response */ any;
export type SetAvailabilityApiV1TrainersMeAvailabilityPostApiArg = {
  trainerAvailabilityCreate: TrainerAvailabilityCreate;
};
export type GetTrainerProfileApiV1TrainersTrainerIdGetApiResponse =
  /** status 200 Successful Response */ TrainerResponse;
export type GetTrainerProfileApiV1TrainersTrainerIdGetApiArg = {
  trainerId: number;
};
export type UpdateTrainerProfileApiV1TrainersTrainerIdPutApiResponse =
  /** status 200 Successful Response */ TrainerResponse;
export type UpdateTrainerProfileApiV1TrainersTrainerIdPutApiArg = {
  trainerId: number;
  trainerUpdate: TrainerUpdate;
};
export type GetTrainerClientsByIdApiV1TrainersTrainerIdClientsGetApiResponse =
  /** status 200 Successful Response */ any;
export type GetTrainerClientsByIdApiV1TrainersTrainerIdClientsGetApiArg = {
  trainerId: number;
  skip?: number;
  limit?: number;
};
export type GetTrainerSessionsApiV1TrainersTrainerIdSessionsGetApiResponse =
  /** status 200 Successful Response */ any;
export type GetTrainerSessionsApiV1TrainersTrainerIdSessionsGetApiArg = {
  trainerId: number;
};
export type GetTrainerStatsByIdApiV1TrainersTrainerIdStatsGetApiResponse =
  /** status 200 Successful Response */ TrainerStats;
export type GetTrainerStatsByIdApiV1TrainersTrainerIdStatsGetApiArg = {
  trainerId: number;
};
export type GetExercisesApiV1ExercisesGetApiResponse =
  /** status 200 Successful Response */ ExerciseResponse[];
export type GetExercisesApiV1ExercisesGetApiArg = {
  skip?: number;
  limit?: number;
  category?: ExerciseCategory | null;
  exerciseType?: ExerciseType | null;
  primaryMuscleGroup?: MuscleGroup | null;
  difficultyLevel?: number | null;
  equipmentNeeded?: string | null;
  maxDurationMinutes?: number | null;
  search?: string | null;
};
export type CreateExerciseApiV1ExercisesPostApiResponse =
  /** status 200 Successful Response */ ExerciseResponse;
export type CreateExerciseApiV1ExercisesPostApiArg = {
  exerciseCreate: ExerciseCreate;
};
export type SeedDefaultExercisesApiV1ExercisesSeedGetApiResponse =
  /** status 201 Successful Response */ any;
export type SeedDefaultExercisesApiV1ExercisesSeedGetApiArg = void;
export type SearchExercisesApiV1ExercisesSearchGetApiResponse =
  /** status 200 Successful Response */ ExerciseResponse[];
export type SearchExercisesApiV1ExercisesSearchGetApiArg = {
  searchTerm: string;
  limit?: number;
};
export type GetPopularExercisesApiV1ExercisesPopularGetApiResponse =
  /** status 200 Successful Response */ ExerciseResponse[];
export type GetPopularExercisesApiV1ExercisesPopularGetApiArg = {
  limit?: number;
};
export type GetExerciseCategoriesApiV1ExercisesCategoriesGetApiResponse =
  /** status 200 Successful Response */ any;
export type GetExerciseCategoriesApiV1ExercisesCategoriesGetApiArg = void;
export type GetMuscleGroupsApiV1ExercisesMuscleGroupsGetApiResponse =
  /** status 200 Successful Response */ any;
export type GetMuscleGroupsApiV1ExercisesMuscleGroupsGetApiArg = void;
export type GetExerciseTypesApiV1ExercisesTypesGetApiResponse =
  /** status 200 Successful Response */ any;
export type GetExerciseTypesApiV1ExercisesTypesGetApiArg = void;
export type GetExercisesByMuscleGroupApiV1ExercisesByMuscleMuscleGroupGetApiResponse =
  /** status 200 Successful Response */ ExerciseResponse[];
export type GetExercisesByMuscleGroupApiV1ExercisesByMuscleMuscleGroupGetApiArg =
  {
    muscleGroup: MuscleGroup;
    includeSecondary?: boolean;
  };
export type GetExercisesByEquipmentApiV1ExercisesByEquipmentEquipmentGetApiResponse =
  /** status 200 Successful Response */ ExerciseResponse[];
export type GetExercisesByEquipmentApiV1ExercisesByEquipmentEquipmentGetApiArg =
  {
    equipment: string;
  };
export type GetBodyweightExercisesApiV1ExercisesBodyweightGetApiResponse =
  /** status 200 Successful Response */ ExerciseResponse[];
export type GetBodyweightExercisesApiV1ExercisesBodyweightGetApiArg = void;
export type GetExerciseApiV1ExercisesExerciseIdGetApiResponse =
  /** status 200 Successful Response */ ExerciseResponse;
export type GetExerciseApiV1ExercisesExerciseIdGetApiArg = {
  exerciseId: number;
};
export type UpdateExerciseApiV1ExercisesExerciseIdPutApiResponse =
  /** status 200 Successful Response */ ExerciseResponse;
export type UpdateExerciseApiV1ExercisesExerciseIdPutApiArg = {
  exerciseId: number;
  exerciseUpdate: ExerciseUpdate;
};
export type DeleteExerciseApiV1ExercisesExerciseIdDeleteApiResponse =
  /** status 200 Successful Response */ any;
export type DeleteExerciseApiV1ExercisesExerciseIdDeleteApiArg = {
  exerciseId: number;
};
export type CreateProgressLogApiV1ProgressPostApiResponse =
  /** status 201 Successful Response */ ProgressLogResponse;
export type CreateProgressLogApiV1ProgressPostApiArg = {
  progressLogCreate: ProgressLogCreate;
};
export type GetClientProgressLogsApiV1ProgressClientClientIdGetApiResponse =
  /** status 200 Successful Response */ ProgressLogResponse[];
export type GetClientProgressLogsApiV1ProgressClientClientIdGetApiArg = {
  clientId: number;
  skip?: number;
  limit?: number;
  logType?: LogType | null;
  exerciseId?: number | null;
  startDate?: string | null;
  endDate?: string | null;
};
export type GetClientProgressStatsApiV1ProgressClientClientIdStatsGetApiResponse =
  /** status 200 Successful Response */ ProgressStats;
export type GetClientProgressStatsApiV1ProgressClientClientIdStatsGetApiArg = {
  clientId: number;
};
export type GetProgressLogApiV1ProgressLogIdGetApiResponse =
  /** status 200 Successful Response */ ProgressLogResponse;
export type GetProgressLogApiV1ProgressLogIdGetApiArg = {
  logId: number;
};
export type UpdateProgressLogApiV1ProgressLogIdPutApiResponse =
  /** status 200 Successful Response */ ProgressLogResponse;
export type UpdateProgressLogApiV1ProgressLogIdPutApiArg = {
  logId: number;
  progressLogUpdate: ProgressLogUpdate;
};
export type DeleteProgressLogApiV1ProgressLogIdDeleteApiResponse = unknown;
export type DeleteProgressLogApiV1ProgressLogIdDeleteApiArg = {
  logId: number;
};
export type CreateProgramApiV1ProgramsPostApiResponse =
  /** status 200 Successful Response */ ProgramResponse;
export type CreateProgramApiV1ProgramsPostApiArg = {
  programCreate: ProgramCreate;
};
export type GetProgramsApiV1ProgramsGetApiResponse =
  /** status 200 Successful Response */ ProgramResponse[];
export type GetProgramsApiV1ProgramsGetApiArg = {
  skip?: number;
  limit?: number;
  status?: ProgramStatus | null;
  difficultyLevel?: DifficultyLevel | null;
  trainerId?: number | null;
  durationWeeksMin?: number | null;
  durationWeeksMax?: number | null;
  search?: string | null;
};
export type GetPopularProgramsApiV1ProgramsPopularGetApiResponse =
  /** status 200 Successful Response */ ProgramResponse[];
export type GetPopularProgramsApiV1ProgramsPopularGetApiArg = {
  limit?: number;
};
export type SearchProgramsApiV1ProgramsSearchGetApiResponse =
  /** status 200 Successful Response */ ProgramResponse[];
export type SearchProgramsApiV1ProgramsSearchGetApiArg = {
  searchTerm: string;
  limit?: number;
};
export type GetTrainerProgramsApiV1ProgramsTrainerTrainerIdGetApiResponse =
  /** status 200 Successful Response */ ProgramResponse[];
export type GetTrainerProgramsApiV1ProgramsTrainerTrainerIdGetApiArg = {
  trainerId: number;
};
export type GetProgramApiV1ProgramsProgramIdGetApiResponse =
  /** status 200 Successful Response */ ProgramResponse;
export type GetProgramApiV1ProgramsProgramIdGetApiArg = {
  programId: number;
};
export type UpdateProgramApiV1ProgramsProgramIdPutApiResponse =
  /** status 200 Successful Response */ ProgramResponse;
export type UpdateProgramApiV1ProgramsProgramIdPutApiArg = {
  programId: number;
  programUpdate: ProgramUpdate;
};
export type DeleteProgramApiV1ProgramsProgramIdDeleteApiResponse =
  /** status 200 Successful Response */ any;
export type DeleteProgramApiV1ProgramsProgramIdDeleteApiArg = {
  programId: number;
};
export type AddExerciseToProgramApiV1ProgramsProgramIdExercisesPostApiResponse =
  /** status 200 Successful Response */ any;
export type AddExerciseToProgramApiV1ProgramsProgramIdExercisesPostApiArg = {
  programId: number;
  programExerciseCreate: ProgramExerciseCreate;
};
export type GetProgramExercisesApiV1ProgramsProgramIdExercisesGetApiResponse =
  /** status 200 Successful Response */ any;
export type GetProgramExercisesApiV1ProgramsProgramIdExercisesGetApiArg = {
  programId: number;
};
export type CreateSessionBookingApiV1SessionsPostApiResponse =
  /** status 200 Successful Response */ SessionBookingResponse;
export type CreateSessionBookingApiV1SessionsPostApiArg = {
  sessionBookingCreate: SessionBookingCreate;
};
export type GetSessionBookingsApiV1SessionsGetApiResponse =
  /** status 200 Successful Response */ SessionBookingResponse[];
export type GetSessionBookingsApiV1SessionsGetApiArg = {
  skip?: number;
  limit?: number;
  clientId?: number | null;
  trainerId?: number | null;
  status?: SessionStatus | null;
  startDate?: string | null;
  endDate?: string | null;
  sessionType?: string | null;
};
export type GetTrainerScheduleApiV1SessionsTrainerTrainerIdScheduleGetApiResponse =
  /** status 200 Successful Response */ any;
export type GetTrainerScheduleApiV1SessionsTrainerTrainerIdScheduleGetApiArg = {
  trainerId: number;
  startDate: string;
  endDate: string;
};
export type GetAvailableTimeSlotsApiV1SessionsTrainerTrainerIdAvailabilityDateGetApiResponse =
  /** status 200 Successful Response */ any;
export type GetAvailableTimeSlotsApiV1SessionsTrainerTrainerIdAvailabilityDateGetApiArg =
  {
    trainerId: number;
    date: string;
    durationMinutes?: number;
  };
export type GetClientSessionsApiV1SessionsClientClientIdSessionsGetApiResponse =
  /** status 200 Successful Response */ SessionBookingResponse[];
export type GetClientSessionsApiV1SessionsClientClientIdSessionsGetApiArg = {
  clientId: number;
  startDate?: string | null;
  endDate?: string | null;
};
export type GetSessionBookingApiV1SessionsBookingIdGetApiResponse =
  /** status 200 Successful Response */ SessionBookingResponse;
export type GetSessionBookingApiV1SessionsBookingIdGetApiArg = {
  bookingId: number;
};
export type UpdateSessionBookingApiV1SessionsBookingIdPutApiResponse =
  /** status 200 Successful Response */ SessionBookingResponse;
export type UpdateSessionBookingApiV1SessionsBookingIdPutApiArg = {
  bookingId: number;
  sessionBookingUpdate: SessionBookingUpdate;
};
export type CancelSessionBookingApiV1SessionsBookingIdCancelPostApiResponse =
  /** status 200 Successful Response */ any;
export type CancelSessionBookingApiV1SessionsBookingIdCancelPostApiArg = {
  bookingId: number;
  reason?: string;
};
export type ConfirmSessionBookingApiV1SessionsBookingIdConfirmPostApiResponse =
  /** status 200 Successful Response */ any;
export type ConfirmSessionBookingApiV1SessionsBookingIdConfirmPostApiArg = {
  bookingId: number;
};
export type CompleteSessionBookingApiV1SessionsBookingIdCompletePostApiResponse =
  /** status 200 Successful Response */ any;
export type CompleteSessionBookingApiV1SessionsBookingIdCompletePostApiArg = {
  bookingId: number;
  sessionNotes?: string | null;
};
export type CreateMealPlanApiV1MealsPostApiResponse =
  /** status 201 Successful Response */ MealPlanResponse;
export type CreateMealPlanApiV1MealsPostApiArg = {
  mealPlanCreate: MealPlanCreate;
};
export type GetMealPlansApiV1MealsGetApiResponse =
  /** status 200 Successful Response */ MealPlanResponse[];
export type GetMealPlansApiV1MealsGetApiArg = {
  skip?: number;
  limit?: number;
  clientId?: number | null;
  dietType?: DietType | null;
  targetCaloriesMin?: number | null;
  targetCaloriesMax?: number | null;
  search?: string | null;
};
export type SearchMealPlansApiV1MealsSearchGetApiResponse =
  /** status 200 Successful Response */ MealPlanResponse[];
export type SearchMealPlansApiV1MealsSearchGetApiArg = {
  searchTerm: string;
  limit?: number;
};
export type GetClientActiveMealPlansApiV1MealsClientClientIdActiveGetApiResponse =
  /** status 200 Successful Response */ MealPlanResponse[];
export type GetClientActiveMealPlansApiV1MealsClientClientIdActiveGetApiArg = {
  clientId: number;
};
export type GetMealPlanApiV1MealsMealPlanIdGetApiResponse =
  /** status 200 Successful Response */ MealPlanResponse;
export type GetMealPlanApiV1MealsMealPlanIdGetApiArg = {
  mealPlanId: number;
};
export type UpdateMealPlanApiV1MealsMealPlanIdPutApiResponse =
  /** status 200 Successful Response */ MealPlanResponse;
export type UpdateMealPlanApiV1MealsMealPlanIdPutApiArg = {
  mealPlanId: number;
  mealPlanUpdate: MealPlanUpdate;
};
export type DeleteMealPlanApiV1MealsMealPlanIdDeleteApiResponse = unknown;
export type DeleteMealPlanApiV1MealsMealPlanIdDeleteApiArg = {
  mealPlanId: number;
};
export type AddRecipeToMealPlanApiV1MealsMealPlanIdRecipesPostApiResponse =
  /** status 200 Successful Response */ any;
export type AddRecipeToMealPlanApiV1MealsMealPlanIdRecipesPostApiArg = {
  mealPlanId: number;
  mealPlanRecipeCreate: MealPlanRecipeCreate;
};
export type GetMealPlanRecipesApiV1MealsMealPlanIdRecipesGetApiResponse =
  /** status 200 Successful Response */ any;
export type GetMealPlanRecipesApiV1MealsMealPlanIdRecipesGetApiArg = {
  mealPlanId: number;
};
export type GetDailyMealPlanApiV1MealsMealPlanIdDayDayNumberGetApiResponse =
  /** status 200 Successful Response */ any;
export type GetDailyMealPlanApiV1MealsMealPlanIdDayDayNumberGetApiArg = {
  mealPlanId: number;
  dayNumber: number;
};
export type GetMealPlanNutritionApiV1MealsMealPlanIdNutritionGetApiResponse =
  /** status 200 Successful Response */ NutritionalSummary;
export type GetMealPlanNutritionApiV1MealsMealPlanIdNutritionGetApiArg = {
  mealPlanId: number;
};
export type GetWeeklyMealPlanApiV1MealsMealPlanIdWeeklyGetApiResponse =
  /** status 200 Successful Response */ WeeklyMealPlan;
export type GetWeeklyMealPlanApiV1MealsMealPlanIdWeeklyGetApiArg = {
  mealPlanId: number;
};
export type DuplicateMealPlanApiV1MealsMealPlanIdDuplicatePostApiResponse =
  /** status 200 Successful Response */ any;
export type DuplicateMealPlanApiV1MealsMealPlanIdDuplicatePostApiArg = {
  mealPlanId: number;
  newName: string;
  clientId?: number | null;
};
export type CreateNotificationTemplateApiV1NotificationsTemplatesPostApiResponse =
  /** status 200 Successful Response */ NotificationTemplateResponse;
export type CreateNotificationTemplateApiV1NotificationsTemplatesPostApiArg = {
  notificationTemplateCreate: NotificationTemplateCreate;
};
export type GetNotificationTemplatesApiV1NotificationsTemplatesGetApiResponse =
  /** status 200 Successful Response */ NotificationTemplateResponse[];
export type GetNotificationTemplatesApiV1NotificationsTemplatesGetApiArg = {
  skip?: number;
  limit?: number;
};
export type GetNotificationTemplateApiV1NotificationsTemplatesTemplateIdGetApiResponse =
  /** status 200 Successful Response */ NotificationTemplateResponse;
export type GetNotificationTemplateApiV1NotificationsTemplatesTemplateIdGetApiArg =
  {
    templateId: number;
  };
export type GetMyNotificationPreferencesApiV1NotificationsPreferencesGetApiResponse =
  /** status 200 Successful Response */ NotificationPreferencesResponse;
export type GetMyNotificationPreferencesApiV1NotificationsPreferencesGetApiArg =
  void;
export type UpdateMyNotificationPreferencesApiV1NotificationsPreferencesPutApiResponse =
  /** status 200 Successful Response */ NotificationPreferencesResponse;
export type UpdateMyNotificationPreferencesApiV1NotificationsPreferencesPutApiArg =
  {
    notificationPreferencesUpdate: NotificationPreferencesUpdate;
  };
export type GetUserNotificationPreferencesApiV1NotificationsPreferencesUserIdGetApiResponse =
  /** status 200 Successful Response */ NotificationPreferencesResponse;
export type GetUserNotificationPreferencesApiV1NotificationsPreferencesUserIdGetApiArg =
  {
    userId: number;
  };
export type SendNotificationApiV1NotificationsSendPostApiResponse =
  /** status 200 Successful Response */ NotificationResponse;
export type SendNotificationApiV1NotificationsSendPostApiArg = {
  sendNotificationRequest: SendNotificationRequest;
};
export type GetMyNotificationsApiV1NotificationsGetApiResponse =
  /** status 200 Successful Response */ NotificationResponse[];
export type GetMyNotificationsApiV1NotificationsGetApiArg = {
  skip?: number;
  limit?: number;
  category?: string | null;
  unreadOnly?: boolean;
};
export type GetAllNotificationsApiV1NotificationsAllGetApiResponse =
  /** status 200 Successful Response */ NotificationResponse[];
export type GetAllNotificationsApiV1NotificationsAllGetApiArg = {
  skip?: number;
  limit?: number;
  userId?: number | null;
  category?: string | null;
  status?: string | null;
};
export type MarkNotificationReadApiV1NotificationsNotificationIdReadPutApiResponse =
  /** status 200 Successful Response */ any;
export type MarkNotificationReadApiV1NotificationsNotificationIdReadPutApiArg =
  {
    notificationId: number;
  };
export type GetNotificationStatsApiV1NotificationsStatsGetApiResponse =
  /** status 200 Successful Response */ NotificationStats;
export type GetNotificationStatsApiV1NotificationsStatsGetApiArg = {
  userId?: number | null;
};
export type HealthCheckHealthGetApiResponse =
  /** status 200 Successful Response */ any;
export type HealthCheckHealthGetApiArg = void;
export type RootGetApiResponse = /** status 200 Successful Response */ any;
export type RootGetApiArg = void;
export type AuthResponse = {
  user_id: number;
  email: string;
  username: string;
  full_name: string | null;
  role: string;
  is_verified: boolean;
  access_token: string;
  refresh_token: string;
  token_type?: string;
  expires_in: number;
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export type RegisterRequest = {
  /** User's email address */
  email: string;
  /** Username */
  username?: string | null;
  /** User's password */
  password: string;
  /** User's full name */
  full_name?: string | null;
  /** User role: client, trainer, or admin */
  role?: string;
};
export type LoginRequest = {
  /** User's email address */
  email: string;
  /** User's password */
  password: string;
};
export type RefreshTokenRequest = {
  refresh_token: string;
};
export type UserProfile = {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  phone: string | null;
  date_of_birth: string | null;
  gender: string | null;
  height: number | null;
  avatar_url: string | null;
  bio: string | null;
  created_at: string;
  last_login: string | null;
};
export type UpdateProfile = {
  full_name?: string | null;
  phone?: string | null;
  date_of_birth?: string | null;
  gender?: string | null;
  /** Height in cm */
  height?: number | null;
  bio?: string | null;
};
export type PasswordChangeRequest = {
  /** Current password */
  current_password: string;
  /** New password */
  new_password: string;
};
export type UserListResponse = {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
};
export type UserResponse = {
  email: string;
  username: string;
  full_name?: string | null;
  phone?: string | null;
  date_of_birth?: string | null;
  gender?: string | null;
  /** Height in cm */
  height?: number | null;
  avatar_url?: string | null;
  bio?: string | null;
  id: number;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string | null;
  last_login: string | null;
};
export type ClientResponse = {
  /** Age in years */
  age?: number | null;
  /** Height in cm */
  height?: number | null;
  /** Fitness level (beginner, intermediate, advanced) */
  fitness_level?: string | null;
  /** Current weight in kg */
  current_weight?: number | null;
  /** Target weight in kg */
  target_weight?: number | null;
  /** Activity level */
  activity_level?: string | null;
  /** List of fitness goals */
  fitness_goals?: string[] | null;
  /** Medical conditions */
  medical_conditions?: string[] | null;
  /** Past or current injuries */
  injuries?: string[] | null;
  /** Current medications */
  medications?: string[] | null;
  /** Preferred workout days */
  preferred_workout_days?: string[] | null;
  /** Preferred workout time */
  preferred_workout_time?: string | null;
  /** Workout experience level */
  workout_experience?: string | null;
  emergency_contact_name?: string | null;
  emergency_contact_phone?: string | null;
  emergency_contact_relationship?: string | null;
  id: number;
  user_id: number;
  assigned_trainer_id: number | null;
  membership_type: string | null;
  membership_start_date: string | null;
  membership_end_date: string | null;
  is_membership_active: boolean;
  created_at: string;
  updated_at: string | null;
  /** Client PIN for self-service access */
  pin_code?: string | null;
};
export type ClientCreate = {
  /** Age in years */
  age?: number | null;
  /** Height in cm */
  height?: number | null;
  /** Fitness level (beginner, intermediate, advanced) */
  fitness_level?: string | null;
  /** Current weight in kg */
  current_weight?: number | null;
  /** Target weight in kg */
  target_weight?: number | null;
  /** Activity level */
  activity_level?: string | null;
  /** List of fitness goals */
  fitness_goals?: string[] | null;
  /** Medical conditions */
  medical_conditions?: string[] | null;
  /** Past or current injuries */
  injuries?: string[] | null;
  /** Current medications */
  medications?: string[] | null;
  /** Preferred workout days */
  preferred_workout_days?: string[] | null;
  /** Preferred workout time */
  preferred_workout_time?: string | null;
  /** Workout experience level */
  workout_experience?: string | null;
  emergency_contact_name?: string | null;
  emergency_contact_phone?: string | null;
  emergency_contact_relationship?: string | null;
};
export type ClientUpdate = {
  /** Age in years */
  age?: number | null;
  /** Height in cm */
  height?: number | null;
  /** Fitness level (beginner, intermediate, advanced) */
  fitness_level?: string | null;
  /** Current weight in kg */
  current_weight?: number | null;
  /** Target weight in kg */
  target_weight?: number | null;
  /** Activity level */
  activity_level?: string | null;
  /** List of fitness goals */
  fitness_goals?: string[] | null;
  /** Medical conditions */
  medical_conditions?: string[] | null;
  /** Past or current injuries */
  injuries?: string[] | null;
  /** Current medications */
  medications?: string[] | null;
  /** Preferred workout days */
  preferred_workout_days?: string[] | null;
  /** Preferred workout time */
  preferred_workout_time?: string | null;
  /** Workout experience level */
  workout_experience?: string | null;
  emergency_contact_name?: string | null;
  emergency_contact_phone?: string | null;
  emergency_contact_relationship?: string | null;
};
export type ClientPinLogin = {
  client_id: number;
  user_id: number;
  full_name: string;
  access_token: string;
  token_type?: string;
  expires_in: number;
};
export type ClientPinAccess = {
  /** Client PIN code */
  pin_code: string;
};
export type ClientProfileUpdate = {
  current_weight?: number | null;
  target_weight?: number | null;
  fitness_goals?: string[] | null;
  /** Client notes or feedback */
  notes?: string | null;
};
export type ClientStats = {
  total_sessions: number;
  completed_sessions: number;
  completed_workouts: number;
  active_programs: number;
  total_workouts_logged: number;
  current_streak_days: number;
  total_weight_change: number | null;
  weight_progress: number | null;
};
export type TrainerResponse = {
  certification?: string | null;
  /** List of specializations */
  specializations?: string[] | null;
  years_of_experience?: number | null;
  /** Years of experience (alias) */
  experience_years?: number | null;
  /** Educational background */
  education?: string | null;
  /** Hourly rate in currency */
  hourly_rate?: number | null;
  /** Professional bio */
  bio?: string | null;
  /** Services offered */
  services_offered?: string[] | null;
  /** Available days of week */
  available_days?: string[] | null;
  /** Available hours range */
  available_hours?: string | null;
  timezone?: string | null;
  /** Combined location */
  location?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  offers_online_training?: boolean;
  offers_in_person_training?: boolean;
  id: number;
  user_id: number;
  is_verified: boolean;
  is_available: boolean;
  average_rating: number;
  total_reviews: number;
  created_at: string;
  updated_at: string | null;
};
export type TrainerCreate = {
  certification?: string | null;
  /** List of specializations */
  specializations?: string[] | null;
  years_of_experience?: number | null;
  /** Years of experience (alias) */
  experience_years?: number | null;
  /** Educational background */
  education?: string | null;
  /** Hourly rate in currency */
  hourly_rate?: number | null;
  /** Professional bio */
  bio?: string | null;
  /** Services offered */
  services_offered?: string[] | null;
  /** Available days of week */
  available_days?: string[] | null;
  /** Available hours range */
  available_hours?: string | null;
  timezone?: string | null;
  /** Combined location */
  location?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  offers_online_training?: boolean;
  offers_in_person_training?: boolean;
  /** Associated user ID (set automatically) */
  user_id?: number | null;
};
export type TrainerUpdate = {
  certification?: string | null;
  /** List of specializations */
  specializations?: string[] | null;
  years_of_experience?: number | null;
  /** Years of experience (alias) */
  experience_years?: number | null;
  /** Educational background */
  education?: string | null;
  /** Hourly rate in currency */
  hourly_rate?: number | null;
  /** Professional bio */
  bio?: string | null;
  /** Services offered */
  services_offered?: string[] | null;
  /** Available days of week */
  available_days?: string[] | null;
  /** Available hours range */
  available_hours?: string | null;
  timezone?: string | null;
  /** Combined location */
  location?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  offers_online_training?: boolean;
  offers_in_person_training?: boolean;
  is_available?: boolean | null;
};
export type TrainerStats = {
  total_clients: number;
  active_clients: number;
  sessions_this_month: number;
  revenue_this_month: number;
  average_rating: number;
  total_sessions: number;
  certification_count: number;
};
export type TrainerDashboard = {
  trainer_info: TrainerResponse;
  stats: TrainerStats;
  today_sessions: {
    [key: string]: any;
  }[];
  upcoming_sessions: {
    [key: string]: any;
  }[];
  recent_clients: {
    [key: string]: any;
  }[];
  notifications: string[];
};
export type TrainerCertificationCreate = {
  name: string;
  issuing_organization?: string | null;
  certification_number?: string | null;
  issue_date?: string | null;
  expiration_date?: string | null;
  is_current?: boolean;
};
export type TrainerCertificationUpdate = {
  name?: string | null;
  issuing_organization?: string | null;
  certification_number?: string | null;
  issue_date?: string | null;
  expiration_date?: string | null;
  is_current?: boolean | null;
};
export type TrainerAvailabilityCreate = {
  /** 0=Monday, 6=Sunday */
  day_of_week: number;
  start_time: string;
  end_time: string;
  is_available?: boolean;
};
export type ExerciseResponse = {
  name: string;
  description?: string | null;
  /** Step-by-step instructions */
  instructions?: string[] | null;
  /** Exercise category */
  category?: string | null;
  /** Target muscle groups */
  muscle_groups?: string[] | null;
  /** Required equipment */
  equipment?: string | null;
  /** Difficulty level */
  difficulty?: string | null;
  /** Exercise tips */
  tips?: string[] | null;
  default_sets?: number | null;
  default_reps?: string | null;
  default_weight?: number | null;
  /** Duration in seconds */
  default_duration?: number | null;
  /** Rest time in seconds */
  rest_time?: number | null;
  calories_per_minute?: number | null;
  safety_tips?: string | null;
  common_mistakes?: string | null;
  /** Alternative exercises */
  alternatives?: string[] | null;
  id: number;
  image_url: string | null;
  video_url: string | null;
  animation_url: string | null;
  is_active: boolean;
  is_public: boolean;
  created_by_trainer_id: number | null;
  created_at: string;
  updated_at: string | null;
};
export type ExerciseCategory =
  | "strength"
  | "cardio"
  | "flexibility"
  | "balance"
  | "sports"
  | "functional"
  | "rehabilitation";
export type ExerciseType =
  | "reps"
  | "time"
  | "distance"
  | "reps_and_weight"
  | "time_and_intensity"
  | "compound"
  | "cardio"
  | "bodyweight";
export type MuscleGroup =
  | "chest"
  | "back"
  | "shoulders"
  | "biceps"
  | "triceps"
  | "forearms"
  | "abs"
  | "obliques"
  | "quads"
  | "hamstrings"
  | "glutes"
  | "calves"
  | "full_body"
  | "cardio";
export type ExerciseCreate = {
  name: string;
  description?: string | null;
  /** Step-by-step instructions */
  instructions?: string[] | null;
  /** Exercise category */
  category?: string | null;
  /** Target muscle groups */
  muscle_groups?: string[] | null;
  /** Required equipment */
  equipment?: string | null;
  /** Difficulty level */
  difficulty?: string | null;
  /** Exercise tips */
  tips?: string[] | null;
  default_sets?: number | null;
  default_reps?: string | null;
  default_weight?: number | null;
  /** Duration in seconds */
  default_duration?: number | null;
  /** Rest time in seconds */
  rest_time?: number | null;
  calories_per_minute?: number | null;
  safety_tips?: string | null;
  common_mistakes?: string | null;
  /** Alternative exercises */
  alternatives?: string[] | null;
  created_by_trainer_id?: number | null;
  is_public?: boolean;
};
export type ExerciseUpdate = {
  name?: string | null;
  description?: string | null;
  instructions?: string[] | null;
  category?: string | null;
  muscle_groups?: string[] | null;
  equipment?: string | null;
  difficulty?: string | null;
  tips?: string[] | null;
  default_sets?: number | null;
  default_reps?: string | null;
  default_weight?: number | null;
  default_duration?: number | null;
  rest_time?: number | null;
  calories_per_minute?: number | null;
  safety_tips?: string | null;
  common_mistakes?: string | null;
  alternatives?: string[] | null;
  is_active?: boolean | null;
  is_public?: boolean | null;
};
export type ProgressLogResponse = {
  /** Exercise ID */
  exercise_id: number;
  /** Workout date and time */
  workout_date: string;
  /** Type of log entry */
  log_type?: string | null;
  workout_type?: string | null;
  sets?: number | null;
  reps?: string | null;
  weight?: number | null;
  distance?: number | null;
  /** Duration in seconds */
  duration?: number | null;
  calories_burned?: number | null;
  intensity_level?: string | null;
  perceived_exertion?: number | null;
  energy_level_before?: number | null;
  energy_level_after?: number | null;
  notes?: string | null;
  form_rating?: number | null;
  location?: string | null;
  weather?: string | null;
  body_weight?: number | null;
  body_fat_percentage?: number | null;
  muscle_mass?: number | null;
  id: number;
  user_id: number;
  max_weight?: number | null;
  max_reps?: number | null;
  best_time?: number | null;
  is_personal_record?: boolean | null;
  improvement_from_last?: number | null;
  created_at?: string | null;
  updated_at?: string | null;
  exercise_name?: string | null;
};
export type ProgressLogCreate = {
  /** Exercise ID */
  exercise_id: number;
  /** Workout date and time */
  workout_date: string;
  /** Type of log entry */
  log_type?: string | null;
  workout_type?: string | null;
  sets?: number | null;
  reps?: string | null;
  weight?: number | null;
  distance?: number | null;
  /** Duration in seconds */
  duration?: number | null;
  calories_burned?: number | null;
  intensity_level?: string | null;
  perceived_exertion?: number | null;
  energy_level_before?: number | null;
  energy_level_after?: number | null;
  notes?: string | null;
  form_rating?: number | null;
  location?: string | null;
  weather?: string | null;
  body_weight?: number | null;
  body_fat_percentage?: number | null;
  muscle_mass?: number | null;
  /** User ID (client) */
  user_id: number;
};
export type LogType = "workout" | "measurement" | "achievement" | "goal";
export type ProgressStats = {
  total_workouts: number;
  total_exercises_performed: number;
  total_duration_hours: number;
  total_calories_burned: number | null;
  personal_records_count: number;
  current_streak_days: number;
  average_workouts_per_week: number;
  most_performed_exercise: string | null;
};
export type ProgressLogUpdate = {
  sets?: number | null;
  reps?: string | null;
  weight?: number | null;
  distance?: number | null;
  duration?: number | null;
  calories_burned?: number | null;
  intensity_level?: string | null;
  perceived_exertion?: number | null;
  energy_level_before?: number | null;
  energy_level_after?: number | null;
  notes?: string | null;
  form_rating?: number | null;
  body_weight?: number | null;
  body_fat_percentage?: number | null;
  muscle_mass?: number | null;
};
export type ProgramTypeEnum =
  | "strength_training"
  | "weight_loss"
  | "muscle_building"
  | "endurance"
  | "flexibility"
  | "sports_specific"
  | "rehabilitation"
  | "general_fitness";
export type ProgramDifficultyEnum = "beginner" | "intermediate" | "advanced";
export type ProgramResponse = {
  name: string;
  description?: string | null;
  /** Program type */
  program_type: ProgramTypeEnum;
  /** Difficulty level */
  difficulty_level: ProgramDifficultyEnum;
  /** Program duration in weeks */
  duration_weeks: number;
  /** Sessions per week */
  sessions_per_week: number;
  /** Program goals */
  goals?: string[] | null;
  /** Target improvements */
  target_metrics?: {
    [key: string]: any;
  } | null;
  notes?: string | null;
  special_instructions?: string | null;
  price?: number | null;
  id: number;
  client_id: number;
  trainer_id: number;
  status: string;
  start_date: string;
  end_date: string | null;
  actual_end_date: string | null;
  current_week: number;
  completion_percentage: number;
  sessions_completed: number;
  total_sessions: number | null;
  weekly_schedule: {
    [key: string]: any;
  } | null;
  exercise_list: number[] | null;
  modifications: string | null;
  is_paid: boolean;
  is_template: boolean;
  created_from_template_id: number | null;
  created_at: string;
  updated_at: string | null;
  client_name?: string | null;
  trainer_name?: string | null;
};
export type ProgramCreate = {
  name: string;
  description?: string | null;
  /** Program type */
  program_type: ProgramTypeEnum;
  /** Difficulty level */
  difficulty_level: ProgramDifficultyEnum;
  /** Program duration in weeks */
  duration_weeks: number;
  /** Sessions per week */
  sessions_per_week: number;
  /** Program goals */
  goals?: string[] | null;
  /** Target improvements */
  target_metrics?: {
    [key: string]: any;
  } | null;
  notes?: string | null;
  special_instructions?: string | null;
  price?: number | null;
  /** Client ID */
  client_id: number;
  /** Weekly workout schedule */
  weekly_schedule?: {
    [key: string]: any;
  } | null;
  /** List of exercise IDs */
  exercise_list?: number[] | null;
};
export type ProgramStatus = "active" | "completed" | "paused" | "cancelled";
export type DifficultyLevel =
  | "beginner"
  | "intermediate"
  | "advanced"
  | "expert";
export type ProgramUpdate = {
  name?: string | null;
  description?: string | null;
  duration_weeks?: number | null;
  sessions_per_week?: number | null;
  status?: string | null;
  current_week?: number | null;
  completion_percentage?: number | null;
  sessions_completed?: number | null;
  weekly_schedule?: {
    [key: string]: any;
  } | null;
  exercise_list?: number[] | null;
  goals?: string[] | null;
  target_metrics?: {
    [key: string]: any;
  } | null;
  notes?: string | null;
  special_instructions?: string | null;
  modifications?: string | null;
};
export type ProgramExerciseCreate = {
  /** Exercise ID */
  exercise_id: number;
  /** Week number */
  week_number: number;
  /** Day number */
  day_number: number;
  /** Exercise order */
  order_in_workout: number;
  sets?: number | null;
  reps?: string | null;
  weight_percentage?: number | null;
  rest_seconds?: number | null;
  duration_seconds?: number | null;
  distance?: number | null;
  notes?: string | null;
};
export type SessionBookingResponse = {
  /** Type of session */
  session_type: string;
  title?: string | null;
  description?: string | null;
  /** Scheduled start time */
  scheduled_start: string;
  /** Scheduled end time */
  scheduled_end: string;
  /** Session duration in minutes */
  duration_minutes?: number;
  location?: string | null;
  room_number?: string | null;
  online_meeting_url?: string | null;
  price?: number | null;
  /** Planned activities */
  planned_activities?: string[] | null;
  id: number;
  client_id: number;
  trainer_id: number;
  actual_start: string | null;
  actual_end: string | null;
  status: string;
  online_meeting_id: string | null;
  is_paid: boolean;
  payment_method: string | null;
  actual_activities: string[] | null;
  trainer_notes_before: string | null;
  trainer_notes_after: string | null;
  client_notes: string | null;
  goals_achieved: string[] | null;
  homework_assigned: string | null;
  next_session_recommendations: string | null;
  client_rating: number | null;
  trainer_rating: number | null;
  client_feedback: string | null;
  trainer_feedback: string | null;
  client_attended: boolean | null;
  trainer_attended: boolean | null;
  original_session_id: number | null;
  reschedule_reason: string | null;
  rescheduled_by: string | null;
  reminder_sent: boolean;
  confirmation_sent: boolean;
  created_at: string;
  updated_at: string | null;
  cancelled_at: string | null;
  client_name?: string | null;
  trainer_name?: string | null;
};
export type SessionBookingCreate = {
  /** Type of session */
  session_type: string;
  title?: string | null;
  description?: string | null;
  /** Scheduled start time */
  scheduled_start: string;
  /** Scheduled end time */
  scheduled_end: string;
  /** Session duration in minutes */
  duration_minutes?: number;
  location?: string | null;
  room_number?: string | null;
  online_meeting_url?: string | null;
  price?: number | null;
  /** Planned activities */
  planned_activities?: string[] | null;
  /** Trainer ID */
  trainer_id: number;
  /** Client ID (if booking for specific client) */
  client_id?: number | null;
};
export type SessionStatus =
  | "scheduled"
  | "confirmed"
  | "in_progress"
  | "completed"
  | "cancelled"
  | "no_show"
  | "rescheduled";
export type SessionBookingUpdate = {
  title?: string | null;
  description?: string | null;
  scheduled_start?: string | null;
  scheduled_end?: string | null;
  duration_minutes?: number | null;
  location?: string | null;
  room_number?: string | null;
  online_meeting_url?: string | null;
  online_meeting_id?: string | null;
  price?: number | null;
  status?: string | null;
  planned_activities?: string[] | null;
  actual_activities?: string[] | null;
  trainer_notes_before?: string | null;
  trainer_notes_after?: string | null;
  client_notes?: string | null;
  goals_achieved?: string[] | null;
  homework_assigned?: string | null;
  next_session_recommendations?: string | null;
};
export type MealPlanResponse = {
  name: string;
  description?: string | null;
  /** Meal plan type */
  plan_type: string;
  /** Plan duration in days */
  duration_days: number;
  /** Dietary restrictions */
  dietary_restrictions?: string[] | null;
  /** Allergens to avoid */
  allergens_to_avoid?: string[] | null;
  target_calories?: number | null;
  target_protein_grams?: number | null;
  target_carbs_grams?: number | null;
  target_fat_grams?: number | null;
  target_fiber_grams?: number | null;
  meals_per_day?: number;
  snacks_per_day?: number;
  /** Food preferences */
  preferences?: string[] | null;
  /** Foods to avoid */
  dislikes?: string[] | null;
  notes?: string | null;
  price?: number | null;
  id: number;
  client_id: number;
  created_by_trainer_id: number | null;
  weekly_meal_plan: {
    [key: string]: any;
  } | null;
  recipes: number[] | null;
  shopping_list: string[] | null;
  is_active: boolean;
  start_date: string | null;
  end_date: string | null;
  adherence_percentage: number;
  is_template: boolean;
  created_from_template_id: number | null;
  is_paid: boolean;
  created_at: string;
  updated_at: string | null;
  client_name?: string | null;
  trainer_name?: string | null;
};
export type MealPlanCreate = {
  name: string;
  description?: string | null;
  /** Meal plan type */
  plan_type: string;
  /** Plan duration in days */
  duration_days: number;
  /** Dietary restrictions */
  dietary_restrictions?: string[] | null;
  /** Allergens to avoid */
  allergens_to_avoid?: string[] | null;
  target_calories?: number | null;
  target_protein_grams?: number | null;
  target_carbs_grams?: number | null;
  target_fat_grams?: number | null;
  target_fiber_grams?: number | null;
  meals_per_day?: number;
  snacks_per_day?: number;
  /** Food preferences */
  preferences?: string[] | null;
  /** Foods to avoid */
  dislikes?: string[] | null;
  notes?: string | null;
  price?: number | null;
  /** Client ID */
  client_id: number;
  /** Weekly meal structure */
  weekly_meal_plan?: {
    [key: string]: any;
  } | null;
  /** List of recipe IDs */
  recipes?: number[] | null;
};
export type DietType =
  | "standard"
  | "vegetarian"
  | "vegan"
  | "keto"
  | "paleo"
  | "low_carb"
  | "mediterranean"
  | "dash"
  | "intermittent_fasting";
export type MealPlanUpdate = {
  name?: string | null;
  description?: string | null;
  duration_days?: number | null;
  dietary_restrictions?: string[] | null;
  allergens_to_avoid?: string[] | null;
  target_calories?: number | null;
  target_protein_grams?: number | null;
  target_carbs_grams?: number | null;
  target_fat_grams?: number | null;
  target_fiber_grams?: number | null;
  meals_per_day?: number | null;
  snacks_per_day?: number | null;
  weekly_meal_plan?: {
    [key: string]: any;
  } | null;
  recipes?: number[] | null;
  preferences?: string[] | null;
  dislikes?: string[] | null;
  notes?: string | null;
  is_active?: boolean | null;
  adherence_percentage?: number | null;
};
export type MealPlanRecipeCreate = {
  /** Recipe ID */
  recipe_id: number;
  /** Day number in the meal plan */
  day_number: number;
  /** Type of meal (breakfast, lunch, etc.) */
  meal_type: string;
  /** Order within the same meal type */
  meal_order?: number;
  /** Number of servings */
  servings?: number;
  /** Portion size description */
  portion_size?: string | null;
  preparation_notes?: string | null;
  substitutions?: string | null;
  /** Whether this meal is optional */
  is_optional?: boolean;
  /** Meal plan ID */
  meal_plan_id: number;
};
export type NutritionalSummary = {
  total_calories?: number;
  total_protein?: number;
  total_carbs?: number;
  total_fat?: number;
  total_fiber?: number;
  protein_percentage?: number;
  carbs_percentage?: number;
  fat_percentage?: number;
};
export type DailyMealPlan = {
  date: string;
  meals: {
    [key: string]: any;
  }[];
  total_calories: number | null;
  total_protein: number | null;
  total_carbs: number | null;
  total_fat: number | null;
  total_fiber: number | null;
  shopping_items: string[] | null;
};
export type WeeklyMealPlan = {
  /** Week number in the plan */
  week_number: number;
  /** Week start date */
  start_date: string;
  /** Week end date */
  end_date: string;
  /** Daily meal plans for the week */
  daily_plans: DailyMealPlan[];
  /** Weekly nutritional summary */
  weekly_nutrition: NutritionalSummary;
  /** Weekly shopping list */
  shopping_list?:
    | {
        [key: string]: any;
      }[]
    | null;
  notes?: string | null;
};
export type NotificationTemplateResponse = {
  /** Template name */
  name: string;
  /** Notification category */
  category: string;
  /** Notification type */
  notification_type: string;
  /** Email subject */
  subject?: string | null;
  /** Push notification title */
  title?: string | null;
  /** Notification body */
  body: string;
  /** Template variables */
  variables?: string[] | null;
  /** Whether template is active */
  is_active?: boolean;
  id: number;
  is_system_template: boolean;
  created_at: string;
  updated_at: string | null;
};
export type NotificationTemplateCreate = {
  /** Template name */
  name: string;
  /** Notification category */
  category: string;
  /** Notification type */
  notification_type: string;
  /** Email subject */
  subject?: string | null;
  /** Push notification title */
  title?: string | null;
  /** Notification body */
  body: string;
  /** Template variables */
  variables?: string[] | null;
  /** Whether template is active */
  is_active?: boolean;
};
export type NotificationPreferencesResponse = {
  /** Enable email notifications */
  email_enabled?: boolean;
  /** Email session reminders */
  email_session_reminders?: boolean;
  /** Email program updates */
  email_program_updates?: boolean;
  /** Email marketing notifications */
  email_marketing?: boolean;
  /** Enable SMS notifications */
  sms_enabled?: boolean;
  /** SMS session reminders */
  sms_session_reminders?: boolean;
  /** SMS for urgent notifications only */
  sms_urgent_only?: boolean;
  /** Enable push notifications */
  push_enabled?: boolean;
  /** Push session reminders */
  push_session_reminders?: boolean;
  /** Push progress updates */
  push_progress_updates?: boolean;
  /** Enable in-app notifications */
  in_app_enabled?: boolean;
  /** Hours before session to remind */
  reminder_hours_before?: number;
  quiet_hours_start?: string | null;
  quiet_hours_end?: string | null;
  timezone?: string | null;
  id: number;
  user_id: number;
  created_at: string;
  updated_at: string | null;
};
export type NotificationPreferencesUpdate = {
  email_enabled?: boolean | null;
  email_session_reminders?: boolean | null;
  email_program_updates?: boolean | null;
  email_marketing?: boolean | null;
  sms_enabled?: boolean | null;
  sms_session_reminders?: boolean | null;
  sms_urgent_only?: boolean | null;
  push_enabled?: boolean | null;
  push_session_reminders?: boolean | null;
  push_progress_updates?: boolean | null;
  in_app_enabled?: boolean | null;
  reminder_hours_before?: number | null;
  quiet_hours_start?: string | null;
  quiet_hours_end?: string | null;
  timezone?: string | null;
};
export type NotificationResponse = {
  /** Recipient user ID */
  user_id: number;
  /** Notification type */
  notification_type: string;
  /** Notification category */
  category: string;
  subject?: string | null;
  title?: string | null;
  /** Notification body */
  body: string;
  /** Recipient email */
  recipient_email?: string | null;
  /** Recipient phone */
  recipient_phone?: string | null;
  /** When to send notification */
  scheduled_for?: string | null;
  /** When notification expires */
  expires_at?: string | null;
  id: number;
  status: string;
  template_id: number | null;
  template_variables: {
    [key: string]: any;
  } | null;
  sent_at: string | null;
  delivered_at: string | null;
  read_at: string | null;
  failed_at: string | null;
  failure_reason: string | null;
  external_id: string | null;
  provider: string | null;
  created_at: string;
  updated_at: string | null;
};
export type SendNotificationRequest = {
  /** Specific user ID (admin only) */
  user_id?: number | null;
  /** Multiple user IDs (admin only) */
  user_ids?: number[] | null;
  /** Notification type */
  notification_type: string;
  /** Notification category */
  category: string;
  subject?: string | null;
  title?: string | null;
  /** Notification body */
  body?: string | null;
  /** Template ID to use */
  template_id?: number | null;
  /** Variables for template */
  template_variables?: {
    [key: string]: any;
  } | null;
  /** When to send notification */
  scheduled_for?: string | null;
};
export type NotificationStats = {
  total_notifications: number;
  sent_notifications: number;
  delivered_notifications: number;
  failed_notifications: number;
  read_notifications: number;
  pending_notifications: number;
};
export const {
  useHealthCheckApiHealthGetQuery,
  useRegisterApiV1AuthRegisterPostMutation,
  useLoginApiV1AuthLoginPostMutation,
  useRefreshTokenApiV1AuthRefreshPostMutation,
  useGetProfileApiV1AuthMeGetQuery,
  useUpdateProfileApiV1AuthMePutMutation,
  useChangePasswordApiV1AuthChangePasswordPostMutation,
  useListUsersApiV1UsersGetQuery,
  useGetUserApiV1UsersUserIdGetQuery,
  useListClientsApiV1ClientsGetQuery,
  useCreateClientProfileApiV1ClientsPostMutation,
  useGetMyClientProfileApiV1ClientsMeGetQuery,
  useUpdateMyClientProfileApiV1ClientsMePutMutation,
  useClientPinLoginApiV1ClientsPinAccessPostMutation,
  useUpdateProfileViaPinApiV1ClientsPinProfileClientIdPutMutation,
  useGetClientProfileApiV1ClientsClientIdGetQuery,
  useUpdateClientProfileApiV1ClientsClientIdPutMutation,
  useAssignTrainerToClientApiV1ClientsClientIdAssignTrainerTrainerIdPostMutation,
  useRegenerateClientPinApiV1ClientsClientIdRegeneratePinPostMutation,
  useGetClientStatsApiV1ClientsClientIdStatsGetQuery,
  useGetTrainerClientsApiV1ClientsTrainerTrainerIdClientsGetQuery,
  useCreateTrainerProfileApiV1TrainersPostMutation,
  useGetAllTrainersApiV1TrainersGetQuery,
  useSearchTrainersApiV1TrainersSearchGetQuery,
  useGetMyTrainerProfileApiV1TrainersMeGetQuery,
  useUpdateMyTrainerProfileApiV1TrainersMePutMutation,
  useGetMyDashboardApiV1TrainersMeDashboardGetQuery,
  useGetMyStatsApiV1TrainersMeStatsGetQuery,
  useGetMyCertificationsApiV1TrainersMeCertificationsGetQuery,
  useAddCertificationApiV1TrainersMeCertificationsPostMutation,
  useUpdateCertificationApiV1TrainersCertificationsCertificationIdPutMutation,
  useGetMyAvailabilityApiV1TrainersMeAvailabilityGetQuery,
  useSetAvailabilityApiV1TrainersMeAvailabilityPostMutation,
  useGetTrainerProfileApiV1TrainersTrainerIdGetQuery,
  useUpdateTrainerProfileApiV1TrainersTrainerIdPutMutation,
  useGetTrainerClientsByIdApiV1TrainersTrainerIdClientsGetQuery,
  useGetTrainerSessionsApiV1TrainersTrainerIdSessionsGetQuery,
  useGetTrainerStatsByIdApiV1TrainersTrainerIdStatsGetQuery,
  useGetExercisesApiV1ExercisesGetQuery,
  useCreateExerciseApiV1ExercisesPostMutation,
  useSeedDefaultExercisesApiV1ExercisesSeedGetQuery,
  useSearchExercisesApiV1ExercisesSearchGetQuery,
  useGetPopularExercisesApiV1ExercisesPopularGetQuery,
  useGetExerciseCategoriesApiV1ExercisesCategoriesGetQuery,
  useGetMuscleGroupsApiV1ExercisesMuscleGroupsGetQuery,
  useGetExerciseTypesApiV1ExercisesTypesGetQuery,
  useGetExercisesByMuscleGroupApiV1ExercisesByMuscleMuscleGroupGetQuery,
  useGetExercisesByEquipmentApiV1ExercisesByEquipmentEquipmentGetQuery,
  useGetBodyweightExercisesApiV1ExercisesBodyweightGetQuery,
  useGetExerciseApiV1ExercisesExerciseIdGetQuery,
  useUpdateExerciseApiV1ExercisesExerciseIdPutMutation,
  useDeleteExerciseApiV1ExercisesExerciseIdDeleteMutation,
  useCreateProgressLogApiV1ProgressPostMutation,
  useGetClientProgressLogsApiV1ProgressClientClientIdGetQuery,
  useGetClientProgressStatsApiV1ProgressClientClientIdStatsGetQuery,
  useGetProgressLogApiV1ProgressLogIdGetQuery,
  useUpdateProgressLogApiV1ProgressLogIdPutMutation,
  useDeleteProgressLogApiV1ProgressLogIdDeleteMutation,
  useCreateProgramApiV1ProgramsPostMutation,
  useGetProgramsApiV1ProgramsGetQuery,
  useGetPopularProgramsApiV1ProgramsPopularGetQuery,
  useSearchProgramsApiV1ProgramsSearchGetQuery,
  useGetTrainerProgramsApiV1ProgramsTrainerTrainerIdGetQuery,
  useGetProgramApiV1ProgramsProgramIdGetQuery,
  useUpdateProgramApiV1ProgramsProgramIdPutMutation,
  useDeleteProgramApiV1ProgramsProgramIdDeleteMutation,
  useAddExerciseToProgramApiV1ProgramsProgramIdExercisesPostMutation,
  useGetProgramExercisesApiV1ProgramsProgramIdExercisesGetQuery,
  useCreateSessionBookingApiV1SessionsPostMutation,
  useGetSessionBookingsApiV1SessionsGetQuery,
  useGetTrainerScheduleApiV1SessionsTrainerTrainerIdScheduleGetQuery,
  useGetAvailableTimeSlotsApiV1SessionsTrainerTrainerIdAvailabilityDateGetQuery,
  useGetClientSessionsApiV1SessionsClientClientIdSessionsGetQuery,
  useGetSessionBookingApiV1SessionsBookingIdGetQuery,
  useUpdateSessionBookingApiV1SessionsBookingIdPutMutation,
  useCancelSessionBookingApiV1SessionsBookingIdCancelPostMutation,
  useConfirmSessionBookingApiV1SessionsBookingIdConfirmPostMutation,
  useCompleteSessionBookingApiV1SessionsBookingIdCompletePostMutation,
  useCreateMealPlanApiV1MealsPostMutation,
  useGetMealPlansApiV1MealsGetQuery,
  useSearchMealPlansApiV1MealsSearchGetQuery,
  useGetClientActiveMealPlansApiV1MealsClientClientIdActiveGetQuery,
  useGetMealPlanApiV1MealsMealPlanIdGetQuery,
  useUpdateMealPlanApiV1MealsMealPlanIdPutMutation,
  useDeleteMealPlanApiV1MealsMealPlanIdDeleteMutation,
  useAddRecipeToMealPlanApiV1MealsMealPlanIdRecipesPostMutation,
  useGetMealPlanRecipesApiV1MealsMealPlanIdRecipesGetQuery,
  useGetDailyMealPlanApiV1MealsMealPlanIdDayDayNumberGetQuery,
  useGetMealPlanNutritionApiV1MealsMealPlanIdNutritionGetQuery,
  useGetWeeklyMealPlanApiV1MealsMealPlanIdWeeklyGetQuery,
  useDuplicateMealPlanApiV1MealsMealPlanIdDuplicatePostMutation,
  useCreateNotificationTemplateApiV1NotificationsTemplatesPostMutation,
  useGetNotificationTemplatesApiV1NotificationsTemplatesGetQuery,
  useGetNotificationTemplateApiV1NotificationsTemplatesTemplateIdGetQuery,
  useGetMyNotificationPreferencesApiV1NotificationsPreferencesGetQuery,
  useUpdateMyNotificationPreferencesApiV1NotificationsPreferencesPutMutation,
  useGetUserNotificationPreferencesApiV1NotificationsPreferencesUserIdGetQuery,
  useSendNotificationApiV1NotificationsSendPostMutation,
  useGetMyNotificationsApiV1NotificationsGetQuery,
  useGetAllNotificationsApiV1NotificationsAllGetQuery,
  useMarkNotificationReadApiV1NotificationsNotificationIdReadPutMutation,
  useGetNotificationStatsApiV1NotificationsStatsGetQuery,
  useHealthCheckHealthGetQuery,
  useRootGetQuery,
} = injectedRtkApi;
